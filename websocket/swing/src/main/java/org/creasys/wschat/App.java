package org.creasys.wschat;

import java.awt.*;
import java.awt.event.*;
import java.net.*;
import java.util.*;
import java.util.concurrent.*;
import javax.swing.*;
import javax.swing.border.*;

import org.eclipse.jetty.websocket.*;
import org.eclipse.jetty.websocket.WebSocket.Connection;
import net.arnx.jsonic.JSON;


public class App {

  private static final URI DEFAULT_SERVER_URI;

  static {
    try {
      DEFAULT_SERVER_URI = new URI("ws://localhost:8080/chat");
    } catch (Exception e) {
      throw new InternalError(e.toString());
    }
  }

  private final Executor send = Executors.newSingleThreadExecutor();
  private final Executor receive = Executors.newSingleThreadExecutor();
  private Connection conn;
  private MainFrame frame;

  public void start(URI serverUri) throws Exception {
    WebSocketClient wsclient = newWebSocketClient();
    wsclient.open(serverUri, new WebSocket.OnTextMessage() {
      @Override
      public void onOpen(Connection conn) {
        App.this.conn = conn;

        SwingUtilities.invokeLater(new Runnable() {
          @Override
          public void run() {
            frame = new MainFrame(App.this);
            frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
            frame.setLocationRelativeTo(null);
            frame.setVisible(true);
          }
        });
      }

      @Override
      public void onClose(int code, String message) {
        System.err.printf("unexpected disconnection: code=%#x [%s]%n", code, message);
        System.exit(1);
      }

      @Override
      public void onMessage(String msg) {
        receive.execute(new ReceiveTalk(frame.talkModel, msg));
      }
    });
  }

  private WebSocketClient newWebSocketClient() throws Exception {
    WebSocketClientFactory webSocketClientFactory = new WebSocketClientFactory();
    webSocketClientFactory.start();
    return webSocketClientFactory.newWebSocketClient();
  }

  void send(String name, String text) {
    send.execute(new SendTalk(conn, name, text));
  }

  static class SendTalk extends SwingWorker<Void, Void> {
    private final Connection conn;
    private final String name;
    private final String text;

    SendTalk(Connection conn, String name, String text) {
      this.conn = conn;
      this.name = name;
      this.text = text;
    }

    @Override
    protected Void doInBackground() throws Exception {
      Map<String, String> map = new HashMap<String, String>();
      map.put("name", name);
      map.put("text", text);
      String json = JSON.encode(map);
      conn.sendMessage(json);
      return null;
    }
  }

  static class ReceiveTalk extends SwingWorker<Map<String, String>, Void> {
    private final TalkModel model;
    private final String msg;

    ReceiveTalk(TalkModel model, String msg) {
      this.model = model;
      this.msg = msg;
    }

    @Override
    protected Map<String, String> doInBackground() throws Exception {
      return JSON.decode(msg);
    }

    @Override
    protected void done() {
      try {
        Map<String, String> msg = get();
        model.add(msg.get("name"), msg.get("text"));
      } catch (Exception e) {
        e.printStackTrace();
      }
    }
  }

  static class MainFrame extends JFrame implements ActionListener {
    private final App app;
    final TalkModel talkModel;

    private final JTextField nameTextfield;
    private final JTextField talkTextfield;

    MainFrame(App app) {
      this.app = app;
      talkModel = new TalkModel();

      nameTextfield = new JTextField();
      talkTextfield = new JTextField();
      JList talkList = new JList();
      JScrollPane talkListPane = new JScrollPane();
      JButton sendButton = new JButton();
      JPanel inputPanel = new JPanel();
      JPanel mainPanel = new JPanel();

      talkList.setModel(talkModel);
      talkList.setCellRenderer(new TalkCellRenderer());

      talkListPane.setViewportView(talkList);
      talkListPane.setBorder(new TitledBorder("Chat"));

      nameTextfield.setColumns(10);

      talkTextfield.setColumns(30);
      talkTextfield.addActionListener(this);

      sendButton.setText("Send");
      sendButton.addActionListener(this);

      inputPanel.setLayout(new FlowLayout());
      inputPanel.add(nameTextfield);
      inputPanel.add(talkTextfield);
      inputPanel.add(sendButton);

      mainPanel.setLayout(new BorderLayout());
      mainPanel.add(talkListPane, BorderLayout.CENTER);
      mainPanel.add(inputPanel, BorderLayout.SOUTH);

      getContentPane().add(mainPanel);
      setTitle("WebSocket Chat Client");
      pack();
    }

    @Override
    public void actionPerformed(ActionEvent event) {
      String name = nameTextfield.getText();
      String text = talkTextfield.getText();
      if (name.isEmpty() || text.isEmpty())
        return;

      talkTextfield.setText("");
      app.send(name, text);
    }

    private static class TalkCellRenderer extends JLabel implements ListCellRenderer {
      public Component getListCellRendererComponent(
          JList list, Object value, int index, boolean selected, boolean hasFocus) {
        String[] talk = (String[]) value;
        String name = talk[0];
        String text = talk[1];
        setText("<html><body>From: <b>" + name + "</b><br>" + text);
        return this;
      }
    }
  }

  static class TalkModel extends DefaultListModel {
    public void add(String name, String text) {
      add(0, new String[] { name, text });
    }
  }

  public static void main(String[] args) throws Exception {
    try {
      UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
    } catch (Exception e) {
      // use default LAF
    }

    URI uri = DEFAULT_SERVER_URI;
    if (args.length > 0) {
      try {
        uri = new URI(args[0]);
      } catch (URISyntaxException e) {
        System.err.println("invalid uri syntax: " + args[0]);
        System.exit(1);
      }
    }

    App app = new App();
    app.start(uri);
  }
}
