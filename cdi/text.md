# CDI 1.0 事始め

従来 Java で DI を用いたい場合には、Spring や Guice に代表される、サードパーティ製の DI コンテナを用いる必要がありました。

CDI は、JavaEE6 の標準仕様に組み込まれた DI と、コンテナが管理する JavaBeans のライフサイクルに関する API 仕様です。標準仕様の一部ですから、JavaEE6 準拠を名乗るアプリケーションサーバー上であれば、サードパーティ製のライブラリに頼ることなく DI を利用することができます。

また、CDI は JavaEE6 を構成するさまざまな仕様を横断した、いわば基礎的な仕様です。JavaEE6自体がモジュラーな構成をとっており、それを繋ぎあわせる役割を担っています。

JavaEE6 を利用するのであれば、CDI を活用しない手はありません。しかし、いくつかの仕様を横断している関係上、その仕様は難解です。今回は、そんな CDI の基本的な使い方を学んでいきます。

# Java EE 6 について

CDIに関する話題に入る前に、JavaEE6 について簡単に解説しておきます。

JavaEE (Java Platform, Enterprise Edition) とは、企業向け Java 標準仕様です。その昔は J2EE と呼ばれていたものの後継にあたります。JavaEE6 は 2009年にリリースされ、現在では主要なアプリケーションサーバーがこの仕様に準拠しています。

EJB や Servlet といった古くからある仕様のバージョンアップや、CDI や JAX-RS といった新しい仕様の取り込みがなされました。方向性としては JavaEE5 時代から取り組まれている開発容易性 (EoD) の促進と、モジュール化、コンテナの軽量化があります。

以下、JavaEE6 の全体図です (JSR-316 より):

![javaee6-architecture.png](/rambo/static/images/f695a885-1bb5-4457-bd29-a3edc4b77539.png)

JavaEE6 の特徴としては

 * 軽量化
 * 拡張性
 * 開発容易性

の 3 つがあげられます。

JavaEE6 で新たに導入された概念として、Profile があります。Profile の導入により、JavaEE の全 API ではなく、必要な API のみを採用したサブセットを定義することができ、結果としてアプリケーションサーバーを軽量化することができます。

JavaEE6 では全 API をカバーする Full Profile と Web アプリケーションの開発に必要な API セットとして Web Profile を定義しています。Web Profileは Servlet や JSP といった Web 関連の技術だけではなく、JPA や JTA といったデータベース接続のための API も含んでいるのが特徴です。

Pruning と呼ばれる概念も追加されました。Pruning とは、残す価値が低い仕様を廃止していくというものです。JavaEE6 では EJB2 の Entity Bean と JAX-RPC が候補に上がっているようです。

開発容易性の向上は、JavaEE6 の前身である JavaEE5 から取り組まれるようになった課題です。XML などを使った外部設定をできるだけ書かずに済むように、Configuration-by-Exception (必要な場合のみデフォルト値を上書きする方法) という方針のもと API の策定がなされています。

EoD 促進の結果として、JavaEE6 の API にはおびただしい数のアノテーションが定義されています。外部設定や手続き的な API を避けようという動きの結果です。ブラックボックス化が行き過ぎていて、逆に分かりにくい部分も決して少なくないというきらいがあります。

また、同じような機能を提供するアノテーションが複数のコンポーネントで定義されていたりするのも混乱の元です。例えば今回取り上げる CDI の DI 機能も、EJB では `@EJB` という EJB 専用のアノテーションが設けられていたり、JAX-RS では `@Context` という JAX-RS 専用のアノテーションが設けられていたり、といった具合です。今後のバージョンアップで、この辺の仕様の整理がなされていくことを期待しています。

## 実装

JavaEE6 準拠を謳うには CTS (Compatibility Test Suite) に通過する必要があります。[Oracle のページ](http://www.oracle.com/technetwork/java/javaee/overview/compatibility-jsp-136984.html)に、公式に認められた JavaEE6 準拠のアプリケーションサーバーが一覧化されています:

サーバー | Full | Web
------- | ---- | --------
Oracle GlassFish Server 3.x | O | O
TMAX JEUS 7 | O | -
IBM WebSphere Application Server | O | -
IBM WebSphere Application Server Community Edition 3.0 | O | -
Fujitsu Interstage Application Server powered by Windows Azure | O | -
Fujitsu Interstage Application Server v10.1 | O | -
Oracle WebLogic Server | O | -
Apache Geronimo 3.0-beta-1 | O | O
JBoss Application Server 7.x | O | O
Hitachi uCosminexus Application Server v9.0 | O | -
JBoss Enterprise Application Platform 6 | O | O
NEC WebOTX Application Server V9.x | O | -
InforSuite Application Server Enterprise Edition V9.1 | O | O
Caucho Resin 4.0.17 | X | O
Apache TomEE 1.0 | X | O
SAP NetWeaver Cloud | X | O
JOnAS | X | O
TongTech TongWeb Application Server 6 | X | O
IBM WebSphere Application Server Version 8.5.5 (Liberty Profile) | X | O

以下、JavaEE6 の中で、比較的使用頻度の高そうな仕様をピックアップして紹介します (CDI は除く)。

## JPA 2.0 (JSR-317)

JavaEE5 から標準仕様の一部となった、RDBMS のデータを扱うフレームワークです。EJB2.0 までの Entity Bean の扱いにくさを受け、サードパーティ製の永続性フレームワークで培われた知見を集約したのが JPA です。

Spring フレームワークの永続層にも JPA のサポートがあり、JavaEE を採用しない場合でも、利用シーンは比較的多いと思われます。

## Bean Validation 1.0 (JSR-303)

JavaBeans のバリデーションのための、メタデータモデル API を採用したフレームワークです。JavaEE6 から標準仕様の一部となりました。

JavaBeans のフィールドなどに対し、制約を表現するアノテーションを付加することでバリデーションを実現します。独自の制約アノテーションを定義することも可能です。

Spring MVC に統合されているので、こちらも比較的利用シーンが多いと思われます。

## EJB 3.1 (JSR-318)

言わずと知れた、EJB のバージョンアップ版です。JavaEE5 で採用された EJB3.0 の流れを組み、より簡単に使えることを目標に機能拡張がなされています。大きな機能追加としては、

 * シングルトンセッションBeanの追加
 * より軽量なサブセット仕様 (EJBLite) の定義
 * .war の中に含められるようになる
 * ローカルインタフェースの定義が不要になる

などが挙げられます。

中・小規模なアプリケーションであっても、高レベルなトランザクション制御 (宣言的トランザクション) にあやかりたい場合など、EJB のお世話になるシーンはそれなりにあると思います。

## なぜ今 JavaEE6 なのか

2013年に JavaEE6 の後継となる JavaEE7 がリリースされました。JavaEE6 の流れを組んだ、新しい仕様です。JavaEE6 では行き届かなかった細かい改善点が数多く見られ、JavaEE6 と JavaEE7 のどちらを使うか選べるのであれば、JavaEE7 を選択すべきだと思います。

しかし [Java EE Compatibility](http://www.oracle.com/technetwork/java/javaee/overview/compatibility-jsp-136984.html) を見ればわかるように、JavaEE7 準拠のアプリケーションサーバーは非常に少ないという現状があります (2015/3 現在)。この現状を踏まえ、現実のプロジェクトで JavaEE7 が採用されるのはまだまだ先になりそうであるということで、今回は比較的実装が多い JavaEE6 を取り上げました。

# 使ってみる

CDI の基本的な機能の一つである DI 機能を使ってみます。

ここでは以下のような構成のオブジェクトツリーを DI で作ってみます:

![di-example-diag.png](/rambo/static/images/b73d23dc-3d4e-4f2b-819f-306214ccb98f.png)

## 手動による DI

先に CDI を使わない場合、自前で依存性の注入を行う場合を考えてみます。

まずは依存される側のクラス (= DI コンテナによってインスタンス生成されるクラス) を定義します:

```java
// Notifier.java
public interface Notifier {
    void send(Message message);
}

// MailNotifier.java
public class MailNotifier implements Notifier {
    @Override
    public void send(Message message) {
        // 本当はメール送信
        System.out.println("send mail [" + message.getSubject() + "] to " + message.getAddress());
    }
}

// NotificationService.java
public class NotificationService {
    
    private Notifier notifier;

    public NotificationService(Notifier notifier) {
        this.notifier = notifier;
    }
    
    public static interface MessageCreator {
        public Message create(String address);
    }
    
    public void notifyRegistration(final String userId) {
        notifyToUser(userId, new MessageCreator() {
            @Override
            public Message create(String address) {
                String subject = "あなたのアカウントが登録されました";
                String body = "新たにあなたのアカウント {userId} が登録されました。以下略";
                Map<String, String> bodyArgs = new HashMap<>();
                bodyArgs.put("userId", userId);
                return new Message(address, subject, body, bodyArgs);
            }
        });
        
        notifyToAdmins(new MessageCreator() {
            @Override
            public Message create(String address) {
                String subject = userId + " が登録されました";
                String body = "新たに {userId} が登録されました。以下略";
                Map<String, String> bodyArgs = new HashMap<>();
                bodyArgs.put("userId", userId);
                return new Message(address, subject, body, bodyArgs);
            }
        });
    }
    
    public void notifyToUser(String userId, MessageCreator creator) {
        String addr = findAddrByUserId(userId);
        notifier.send(creator.create(addr));
    }
    
    public void notifyToAdmins(final MessageCreator creator) {
        for (String addr : findAdminAddresses())
            notifier.send(creator.create(addr));
    }
    
    private List<String> findAdminAddresses() {
        // 本当はDB参照
        return Arrays.asList("aaa@example.com", "bbb@example.com");
    }
    
    private String findAddrByUserId(String userId) {
        // 本当はDB参照
        return userId + "@example.com";
    }
}
```

手動の場合、どうにか自力で `MailNotifier` のインスタンスと、`NotificationService` のインスタンスを得る必要があります。今回はオブジェクトツリーのルートにあたる `MyServlet` から new してインスタンス化します。

```java
@WebServlet(urlPatterns = { "/di/cdi" })
public class MyServlet extends HttpServlet {

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {
        Notifier notifier = new MailNotifier();
        NotificationService notification = new NotificationService(notifier);

        notification.notifyRegistration("test1");
        notification.notifyRegistration("test2");

        PrintWriter pw = resp.getWriter();
        pw.println("hello, please check stdout");
    }
}
```

`NotificationService` のコンストラクタで `Notifier` への依存性を注入しています。この実装では `NotificationService` から `Notifier` への依存性は外部から注入できますが、`MyServlet` から `NotificationService`, `Notifier` への依存性は外部から注入することができません。この程度の規模であれば少しの修正で対応できるでしょうが、規模が大きくなってくると、実装の煩わしさが常について回ります。

また、今回は `doGet` の中で各インスタンスを new しましたが、もっと広いスコープでインスタンス化し、それを使いまわしたい場合には、別の工夫が必要になってきます。

## CDI による DI

CDI では、依存される側のクラスについては何もアノテーションをつける必要はありません [^1]。依存する側のクラスの定義を、CDI を利用するよう変えていきます:

```java
// NotificationService.java
public class NotificationService {

    @Inject
    private Notifier notifier;
    
    public static interface MessageCreator {
        public Message create(String address);
    }
    // ... 以下略
}

// MyServlet.java
@WebServlet(urlPatterns = { "/di/cdi" })
public class MyServlet extends HttpServlet {

    @Inject
    private NotificationService notification;

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {
        // ... 以下略
    }
}
```

ここでは簡単に実行できるように Servlet にしました。CDI では依存性のルートに当たるクラスについては、いくつかの条件が設けられています:

 * Servlet や EJB など、JavaEE アプリケーションサーバーによってライフサイクルを管理されるもの
 * CDI のスコープを明示していること

といったところで、その一つを満たせばよいことになっています。

これ以外は特に設定なども必要ありません。依存性を注入したい場所に `@Inject` をつけておけば、アプリケーションサーバー上で稼働する CDI コンテナによって依存関係が解決されます。

ただし CDI 自体を有効にするためのファイルだけ作っておく必要があります。[^1]

```
$ touch src/main/webapp/WEB-INF/beans.xml
```

## JSR-330 との関係について

実は CDI の DI 仕様というのは、別の JSR で策定された仕様です。ここまで「CDI の DI」と呼んできた機能は、厳密に言うと JSR-330 (Dependency Injection for Java) という仕様で定義された DI 機能です。CDI の DI 部分は JSR-330 に乗っかっていて、そこにコンテキストや DI に関する追加仕様、デコレータ、イベントやデプロイの仕様を追加したのが CDI (JSR-299) になります。

もともとは CDI 一本で行こうとしていたところが、CDI の仕様が膨らんできたことで、DI だけを独立した仕様にするという動きが出てきたようです。

DI コンテナの実装である Google Guice は JSR-330 の参照実装ですが、JSR-299 の参照実装ではありません。一応この辺の境もあるということを覚えておけば、いいことがあるかもしれません（ないかもしれません）。

# CDI 1.0 の仕様 (JSR-299)

CDI 仕様では以下の機能を提供します:

 1. オブジェクトの明確なコンテキスト
 2. 依存性の注入: コンテキストを持つオブジェクトに対して自動的に依存性を注入する
 3. JavaEE のコンポーネント同士を粗結合に接続し、モジュール化を促進する
 4. EL 式から直接参照できるようにする
 5. CDI により注入されるオブジェクトのデコレーション
 6. タイプセーフなインターセプタのバインディングを提供する
 7. イベント通知
 8. Servlet API (Web) 向けに定義されたコンテキスト
 9. CDI を拡張するための SPI

これは JSR-299 の冒頭に箇条書きされているものです。1, 2 の仕様を軸として、デコレータ、インターセプタ、イベント通知などの機能を統合し、EL式や Servlet といった他の仕様との兼ね合いも意識したものになっています。この辺がサードパーティ製の DI コンテナである Spring や Guice とは単純には比較できないところになります (カバーしている領域が違う)。

## コンテキスト

コンテナが管理する JavaBeans の明確なライフサイクル (スコープ) を提供する機能です。CDI のもっとも基本的な機能のひとつです。明確なスコープが設定されたオブジェクトは、

 * スコープの開始と終了にあわせて自動的にインスタンス化され、自動的に破棄される
 * 複数のクライアントから同時に参照可能なスコープを持つオブジェクトは、その状態を自動的に共有される

CDI 1.0 仕様では 5 つのスコープがあらかじめ定義されています:

型 | スコープ
-- | -------
@ApplicationScoped | アプリケーションの起動から終了まで
@SessionScoped | セッション (HttpSession) の開始から終了まで
@RequestScoped | リクエストの開始から終了まで
@ConversationScoped | 会話スコープ。任意の長さ
@Dependent | 依存元のスコープに依存。擬似スコープ

※厳密にはもっと詳しい決まりがあります。JSR-299 の 6.7. Context management for built-in scopes を参照

すべてアノテーションが `javax.enterprice.context` パッケージに定義されています。

`@ApplicationScoped`, `@SessionScoped`, `@RequestScoped` の動きを見てみます。まずはスコープを指定したクラス (依存される側のクラス) を定義します。

```java
// Counter.java
@ApplicationScoped
public class Counter implements Serializable {
    private static final long serialVersionUID = 1L;
    
    @Inject
    private CountHolder holder;
    @Inject
    private CountWriter cw;
    
    public String count() {
        return cw.toString(holder.next());
    }
    
    @PostConstruct
    public void init() {
        System.out.println(this + "::init (ApplicationScoped)");
    }
    @PreDestroy
    public void destroy() {
        System.out.println(this + "::destroy (ApplicationScoped)");
    }
}

// CountHolder.java
@SessionScoped
public class CountHolder implements Serializable {
    private static final long serialVersionUID = 1L;
    
    private int count;
    
    public synchronized int next() {
        return ++count;
    }
    
    @PostConstruct
    public void init() {
        System.out.println(this + "::init (SessionScoped)");
    }
    @PreDestroy
    public void destroy() {
        System.out.println(this + "::destroy (SessionScoped)");
    }
}

// CountWriter.java
@RequestScoped
public class CountWriter {
    public String toString(int count) {
        return "count: " + count;
    }
    
    @PostConstruct
    public void init() {
        System.out.println(this + "::init (RequestScoped)");
    }
    @PreDestroy
    public void destroy() {
        System.out.println(this + "::destroy (RequestScoped)");
    }
}
```

もっとも大きいスコープである `@ApplicationScoped` から、より狭いスコープである `@SessionScoped` 及び `@RequestScoped` に依存しています。`@ApplicationScoped` なオブジェクトが破棄される前に、より狭いスコープのオブジェクトは生成/破棄が行われることになります。

`@ApplicationScoped` に依存するクラスを定義します。今回も Servlet として定義しています。

```java
@WebServlet(urlPatterns = { "/lifecycle/scope" })
public class MyServlet extends HttpServlet {

    @Inject
    private Counter counter;

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        PrintWriter pw = resp.getWriter();
        pw.println(counter.count());
    }
}
```

デプロイし、このブラウザから Servlet にアクセスすると、標準出力にいくつか出力されます:

```
情報:   org.creasys.cditutor.lifecycle.scope.Counter@2347877e::init (ApplicationScoped)
情報:   org.creasys.cditutor.lifecycle.scope.CountHolder@3dfe6893::init (SessionScoped)
情報:   org.creasys.cditutor.lifecycle.scope.CountWriter@983aab1::init (RequestScoped)
情報:   org.creasys.cditutor.lifecycle.scope.CountWriter@983aab1::destroy (RequestScoped)
```

初めてのアクセスなので `@ApplicationScoped` が初期化されました。セッションが開始したので `@SessionScoped` も初期化されています。`@RequestScoped` は初期化され、破棄されていることが分かります。

別のブラウザからアクセスしてみます:

```
情報:   org.creasys.cditutor.lifecycle.scope.CountHolder@96b5cc4::init (SessionScoped)
情報:   org.creasys.cditutor.lifecycle.scope.CountWriter@67974cb0::init (RequestScoped)
情報:   org.creasys.cditutor.lifecycle.scope.CountWriter@67974cb0::destroy (RequestScoped)
```

`@ApplicationScoped` は初期化されていないことが分かります。`@SessionScoped` が初期化されたのは、別ブラウザからのアクセスなので新しいセッションが開始したためです。

最初にアクセスしたブラウザからもう一度アクセスしてみます:

```
情報:   org.creasys.cditutor.lifecycle.scope.CountWriter@6824a077::init (RequestScoped)
情報:   org.creasys.cditutor.lifecycle.scope.CountWriter@6824a077::destroy (RequestScoped)
```

`@RequestScoped` だけが初期化・破棄されています。すでにセッションが開始しているため、`@SessionScoped` は以前に初期化されたものが利用されています。

このように、CDI ではスコープの大小関係を意識せずにつなぐことができるようになっています。この機構により、オブジェクトのライフサイクルを単純に考え、そのまま実装に起こすことができます。Web 開発であれば、

 * 画面からのリクエストに関連する情報 (入力など): `@RequestScoped`
 * セッションが続く間保持したい情報 (ログイン情報など): `@SessionScoped`
 * ステートレスなロジッククラス: `@ApplicationScoped`

といった具合にスコープを指定しさえしておけば、あとは CDI がオブジェクトのライフサイクルを管理し、適切に依存性の注入までしてくれるというわけです。

また、CDI では独自のスコープを定義できるようになっています。組み込みのスコープだけで事足りない場合には、独自のスコープを定義し、対象の JavaBeans に付加すれば CDI にそのライフサイクルを管理させることができます。

## デコレータ

いわゆる GoF パターンの Decorator パターンを実装するために用意された CDI の機能です。業務ロジックが実装された既存の Beans をオーバーラップし、追加の処理を実行することができるようになります。機能的には後述のインターセプタと似ていますが、デコレータが業務ロジックを実装するために利用するのに対し、インターセプタは *業務ロジックに関連しない横断要素を実装するための仕組み* という目的で利用します。

例を見てみます。次のようなクラス構成を考えてみます:

![decorator-diag.png](/rambo/static/images/16e4dc24-9472-4d92-808f-105b9a7bc214.png)

デコレータがデコレートする対象は interface である必要があります。ここでは `Document` インタフェースを定義し、その実装クラスとして `DBStoredDocument` クラスを定義しています。 `FormattedDocument` がデコレータです。

まずデコレートされる側の定義です:

```java
// Document.java
public interface Document {
    String getText();
}

// DBStoredDocument.java
public class DBStoredDocument implements Document {
    @Override
    public String getText() {
        return "db  stored    document";
    }
}
```

次にデコレータです:

```java
@Decorator
public class FormattedDocument implements Document, Serializable {
    private static final long serialVersionUID = 1L;
    
    @Inject @Delegate
    private Document doc;
    
    @Override
    public String getText() {
        String text = doc.getText();
        return format(text);
    }
    
    private static String format(String text) {
        // great formatting process...
        return text.replaceAll("  *", " ");
    }
}
```

Document が返す生のテキストを整形して返すという想定です。今回の実装では、連続するスペースを 1 つにまとめるという取ってつけたような実装としています。

デコレータを CDI に認識させるには、デコレータを *有効化* する必要があります。CDI1.0 では beans.xml の `<decorators>` 要素にエントリを追加することで、デコレータを有効化できます: [^1]

```xml
<?xml version="1.0" encoding="UTF-8"?>
<beans xmlns="http://java.sun.com/xml/ns/javaee"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xsi:schemaLocation="http://java.sun.com/xml/ns/javaee http://java.sun.com/xml/ns/javaee/beans_1_0.xsd">
    <decorators>
        <class>org.creasys.cditutor.decorator.FormattedDocument</class>
    </decorators>
</beans>
```

最後にデコレータを使うクラスの実装です:

```java
@WebServlet(urlPatterns = "/decorator")
public class MyServlet extends HttpServlet {
    @Inject
    private Document doc;

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        PrintWriter pw = resp.getWriter();
        pw.println("<html><body>");
        pw.println(doc.getText().replaceAll(" ", "&nbsp;"));
        pw.println("</body></html>");
    }
}
```

実行すると次のような結果が得られます。半角スペースが 1 つにまとめられているのが分かります。

```
db stored document
```

## インターセプタ

いわゆる AOP (アスペクト指向プログラミング) を実装するために用意された CDI の機能です。業務ロジックが実装された Beans の処理に割り込み、業務ロジックには直接関係のない、複数のモジュールを横断する処理を記述するのに利用できます。代表的な使用例としては、ロギング、認証チェックなどがあります。

ありがちな例として、メソッドの開始・終了ログを出力するインターセプタを定義してみます。

まず、インターセプタを識別するための `@InterceptorBinding` を定義します:

```java
@InterceptorBinding
@Retention(RUNTIME)
@Target({METHOD, TYPE})
public @interface Traced {
}
```

この `@Traced` アノテーションが付加されたインターセプタが、 `@Traced` アノテーションが付加されたクラス、メソッドで有効化されるようなイメージです。

`@Traced` アノテーションが付加されたクラス、メソッドで動作するインターセプタ本体を実装します:

```java
@Traced @Interceptor
public class Tracer {
    @AroundInvoke
    public Object aroundInvoke(InvocationContext ic) throws Exception {
        Method m = ic.getMethod();
        Logger logger = Logger.getLogger(m.getDeclaringClass().getName());
        logger.log(Level.INFO, "[Start]: {0}", m.getName());
        try {
            return ic.proceed();
        } catch (Exception e) {
            logger.log(Level.WARNING, "[Suspend]: {0}, exception={1}", new Object[] { m.getName(), e });
            throw e;
        } finally {
            logger.log(Level.INFO, "[End]: {0}", m.getName());
        }
    }
}
```

`ic.proceed()` が、インターセプトした対象の処理を実行している部分です。他がインターセプタ独自の実装 (ロギング) になります。

インターセプタを利用するには、デコレータ同様、 *有効化* が必要になります。CDI 1.0 では (これまたデコレータと同様) beans.xml の `<interceptors>` 要素にエントリを追加する必要があります: [^1]

```xml
<?xml version="1.0" encoding="UTF-8"?>
<beans xmlns="http://java.sun.com/xml/ns/javaee"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xsi:schemaLocation="http://java.sun.com/xml/ns/javaee http://java.sun.com/xml/ns/javaee/beans_1_0.xsd">
    <interceptors>
        <class>org.creasys.cditutor.interceptor.Tracer</class>
    </interceptors>
</beans>
```

最後に、インターセプタを使うクラスの実装です:

```java
// Beans.java
public class Beans {
    private static Logger logger = Logger.getLogger(Beans.class.getName());

    @Traced
    public void tracedMethod() {
        logger.log(Level.INFO, "in tracedMethod");
    }
    
    public void notTracedMethod() {
        logger.log(Level.INFO, "in notTracedMethod");
    }
}

// MyServlet.java
@WebServlet(urlPatterns = "/interceptor")
public class MyServlet extends HttpServlet {
    
    @Inject Beans beans;

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        beans.tracedMethod();
        beans.notTracedMethod();
        resp.getWriter().println("see stdout");
    }
}
```

標準出力には以下のように出力されます:

```
情報:   [Start]: tracedMethod
情報:   in tracedMethod
情報:   [End]: tracedMethod
情報:   in notTracedMethod
```

`tracedMethod` ではインターセプタが介入しており、 `notTracedMethod` では介入していない様子が見て取れます。

## イベント

CDI 上で動作するモジュール同士でイベント通知するための機能が CDI に用意されています。明示的なリスナーの登録が不要で、通知先は、イベントオブジェクトの型によって判断されます。

例を見てみます。まず、イベント通知を受ける側の実装です:

```java
// LoggedInEvent.java
public class LoggedInEvent {
    private final String userId;
    
    public LoggedInEvent(String userId) {
        this.userId = userId;
    }
    
    public String getUserId() {
        return userId;
    }
}

// CurrentUser.java
@SessionScoped
public class CurrentUser implements Serializable {
    private static final long serialVersionUID = 1L;
    
    private String userId;
    private boolean admin;
    
    public void onLoggedIn(@Observes LoggedInEvent event) {
        System.out.println("[OBSERVER] thread=" + Thread.currentThread().getId());
        this.userId = event.getUserId();
        this.admin = isAdmin(userId);
    }
    
    private boolean isAdmin(String userId) {
        return Objects.equals(userId, "admin");  // 本当はDBアクセス
    }
    
    public boolean isGuest() {
        return userId == null;
    }
    
    public boolean isAdmin() {
        return admin;
    }
}
```

`LoggedInEvent` はイベントそのものを表現するクラスです。ログインユーザーのユーザーIDを持ちます。

ログイン中のユーザー情報を保持するクラス `CurrentUser` を `@SessionScoped` で定義しています。 `onLoggedIn` メソッドがイベント通知を受けるメソッドです。

ポイントは *仮引数に `@Observes` アノテーションをつけること* です。

次に通知する側です:

```java
@WebServlet(urlPatterns = "/event")
public class MyServlet extends HttpServlet {

    @Inject Event<LoggedInEvent> login;
    @Inject CurrentUser user;

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        String uid = req.getParameter("uid");
        if (uid == null) {
            HttpSession s = req.getSession();
            if (s != null)
                s.invalidate();
        }
        else {
            req.getSession(true);
            login.fire(new LoggedInEvent(uid));
            System.out.println("[SENDER] thread=" + Thread.currentThread().getId());
        }

        resp.getWriter().println("guest=" + user.isGuest() + ", admin=" + user.isAdmin());
    }
}
```

`login.fire(new LoggedInEvent(uid))` の部分がイベント通知を行っているところです。 `login` は `Event` 型のフィールドで、イベント引数として `LoggedInEvent` を指定しています。

`login.fire(...)` により、`@Observes LoggedInEvent xxx` という引数を持つメソッドに、イベントが通知されます。

# DI について、もう少し

DI は CDI の中でもっとも利用する頻度の高い機能の１つです。先の例では DI の簡単な使い方について学びました。ここではもう少し突っ込んだ使い方、仕様の詳細などについて触れていきます。

## DI 方法

先の例ではフィールドに `@Inject` を付加することで DI させました。`@Inject` はフィールドの他に、メソッド、コンストラクタに付加することができます。

```java
public class NotificationService {
    @Inject
    private Notifier notifier;  // フィールドインジェクション
    
    @Inject
    public NotificationService(RetryPolicy retry) { ... }  // コンストラクタインジェクション
    
    @Inject
    void init(@Users EntityMangerFactory emf) { ... }  // メソッドインジェクション
}
```

フィールド、メソッド、コンストラクタすべてに共通する取り決めとして、アクセス修飾子はなんでも構いません。private, package-private, protected,public 全て使えます。

DI の実行順序は

 1. コンストラクタ
 2. フィールド
 3. メソッド

です。フィールド、メソッドについては親クラスに対する DI が先に実施され、サブクラスに対する DI が後に実施されます。同クラス内の同メンバーの DI順序 (例: クラス A のフィールド x, y に対する DI 順序) は、仕様では規定されていません。

## DI で注入可能な型の要件

JSR-299 の 2.2.1 Legal bean types にまとめられています:

 * インタフェース、具象クラス、抽象クラス、final が付けられたクラス、final メソッドを持つクラス
 * 具体的な型、または型変数でパラメタライズされたクラス
 * 配列
 * プリミティブ型 (対応するラッパー型と同列に扱われる)
 * raw 型 (型変数を除いたジェネリック型)

以上のいずれかを満たせば、DI によって注入できる型となります。これを見ると型を表現するほとんどの言語要素が DI で注入可能な型であると言えます。

JSR-299 によれば、「型変数」がこれに該当しないと記載されています。つまりこんなことができません:

```java
public class Foo<T> {
    @Inject
    T obj;
}
```

## Produces

これまで取り上げてきた `@Inject` で注入するオブジェクトは、すべてコンテナが直接生成したインスタンスを利用してきました。実際にはファクトリメソッドで生成したインスタンスを利用したい場合もあります。

この要件を満たすのに利用できるのが `@Produces` です。

```java
public class LoggerProduces {
    @Produces
    public Logger getLogger(InjectionPoint ip) {
        String name = ip.getMember().getDeclaringClass().getSimpleName();
        return Logger.getLogger(name);
    }
}
```

`Logger` を生成する `@Produces` メソッドを定義しました。

`InjectionPoint` クラスは、`@Inject` が付加された場所を表現するオブジェクトです。`@Produces` が付加されたメソッドの引数として受け取ることができます。

使ってみます:

```java
@WebServlet(urlPatterns = { "/produces" })
public class MyServlet extends HttpServlet {
    
    @Inject
    private Logger logger;

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        logger.log(Level.INFO, "アクセスされたよ");
        logger.log(Level.SEVERE, "やばいよ");
        
        PrintWriter pw = resp.getWriter();
        pw.println("hello, please check stdout");
    }
}
```

例によってサーブレットです。このサーブレットにアクセスすると:

```
情報:   アクセスされたよ
重大:   やばいよ
```

という出力が得られます。

## Qualifier

これまで見てきた DI の例は、全て CDI の *Typesafe Resolution* という仕組みに則って、その依存性が解決されてきました。依存する側とされる側との間で型が矛盾しなければ (= 代入可能であれば)、その間に依存性を注入するというものです。この Typesafe Resolution は DI だけでなくデコレータやインターセプタ、イベント通知などにも適用される仕組みです。

しかしこれだけではカバーできない場合もあります。例えばデータソースが複数の用途で分かれているとして、

```java
// DataSources.java
public class DataSources {
    @Produces public DataSource forUser() { ... }
    @Produces public DataSource forPayment() { ... }
}

// DataClient.java
public class DataClient {
    @Inject DataSource user;
    @Inject DataSource payment;
}
```

という風に書いていたとします。`user` と `payment` は全く別のデータソース (例えば DB が異なる) とします。

Typesafe Resolution だけでは、 `user` と `payment` には同じインスタンスに依存するものとして解決されてしまい、期待する動作とはなりません。

そもそもこのプログラムはデプロイできません。同じ型に対する `@Produces` メソッドが複数存在するため、コンテナがどちらのメソッドを使って依存性を解決すればよいかが判断できないためです。

こういった自体を解決するために用意されているのが `@Qualifier` です。Qualifier は基本的にアプリケーションの要件に応じて自分で定義していきます。ここでは `@User` と `@Payment` を定義してみます:

```java
// User.java
@Qualifier
@Retention(RUNTIME)
@Target({METHOD, FIELD, PARAMETER, TYPE})
public @interface User {
}

// Payment.java
@Qualifier
@Retention(RUNTIME)
@Target({METHOD, FIELD, PARAMETER, TYPE})
public @interface Payment {
}
```

この Qualifier を使って、依存性のあいまいさを排除します:

```java
// DataSources.java
public class DataSources {
    @Produces @User public DataSource forUser() { ... }
    @Produces @Payment public DataSource forPayment() { ... }
}

// DataClient.java
public class DataClient {
    @Inject @User DataSource user;
    @Inject @Payment DataSource payment;
}
```

ファクトリメソッドと注入ポイントそれぞれに `@User` と `@Payment` を付加しました。これによってコンテナはどこに何を注入すればよいかを判断できるようになります。

# クライアントサイドプロキシ

スコープが異なるオブジェクトの間に依存関係を持たせると、通常のインスタンスアクセスでは同時アクセスで問題が発生します。同時アクセスでなくとも、何かしらの方法でインスタンスをすり替えるような仕組みが必要です。

例えば:

```java
public class Client {
    @Inject Foo foo;
    public void method(String s) {
        System.out.println(s + ": " + foo.next());
    }
}

@ApplicationScoped
public class Foo {
    @Inject Bar obj;
    public int next() { return obj.next(); }
}

@SessionScoped
public class Bar {
    private int i;
    public int next() { return ++i; }
}
```

こんな依存関係を組んでいたとします。`Client` のインスタンスを複数作ったとしても、`Foo` のインスタンスは `@ApplicationScoped` なので 1 つしか作られません。また `Foo` が依存する `Bar` は呼び出し元のセッションに応じて切り替える必要があります。

```java
// セッション1
onSession(() -> {
    Client c = new Client();
    c.method("session1");
    c.method("session1");
});
// セッション2
onSession("session2", () -> {
    Client c = new Client();
    c.method("session2");
});
```

コメント「セッション１」「セッション２」がそれぞれ別のセッション上で動くものとします。この時期待する結果は:

```
session1: 1
session1: 2
session2: 1
```

です。プログラムをぱっと見た感じではそう動きそうにありませんが、実際 CDI 上でこのようなプログラムを組むと、期待どおりに動きます。なぜでしょうか？

このようなスコープの違う異なるオブジェクト同士を連携させるための仕組みが *クライアントプロキシ* です。

先程の例は、実際には以下のように動いています:

![client-proxy-seq.png](/rambo/static/images/ce0c2aa5-accd-43fd-8806-70cea1fbcc84.png)

`@ApplicationScoped`, `@SessionScoped` でライフサイクルが明示されたオブジェクトに対する呼び出しは、そのプロキシオブジェクトの呼び出しになります。プロキシ内では呼び出し元や呼び出されたスレッドなどを元に適切なオブジェクトを生成、選択し、処理を移譲します。

ライフサイクルの例で出したプログラムを書き換え、クライアントプロキシの存在を確認してみます:

```java
// MyServlet.java
@WebServlet(urlPatterns = { "/lifecycle/scope" })
public class MyServlet extends HttpServlet {
    @Inject
    private Counter counter;
    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        PrintWriter pw = resp.getWriter();
        pw.println(counter.getClass());
    }
}
```

これを実行すると、画面には

```
class org.creasys.cditutor.lifecycle.scope.Counter$Proxy$_$$_WeldClientProxy
```

と表示されます。`Counter` クラスの名前ではなく、実行時に自動生成されたプロキシクラスの名前が出力されています。Weld というのは Glassfish で利用されている CDI 実装です。

# まとめ

だらだらと CDI 1.0 の基本的な使い方を追ってきました。大体の雰囲気は掴んでもらえたんじゃないかと思います。

独断と偏見で、基本的な使い方は外れるだろということで、今回は触れなかった仕様がいくつかあります。デプロイに関する仕様、CDI の拡張モジュールを作るための仕様などです。デプロイに関する仕様はデバッグ時には役立つ知識になるでしょうし、CDI の拡張モジュールは独自のスコープを定義するときに関係してきます。

CDI 仕様は、仕様書ページ数こそ 100 ページ程度とさほど多いものではないものの、機能はそれなりに豊富で、かつ他の仕様にまたがっている部分が多々あるため、複雑です。かといって「複雑で使い物にならない！」というものではなく、「DI や Context だけ使おう」といった具合に、分かりやすいところだけでも十分に使いでのある仕様だと思います。

# 参考URL

* [CDI 1.0 仕様書](http://docs.jboss.org/cdi/spec/1.0/html/)
* [Contexts & Dependecy Injection for Java](http://cdi-spec.org/)
* [Java EE 6 Technologies](http://www.oracle.com/technetwork/java/javaee/tech/javaee6technologies-1955512.html)

[^1]: CDI1.1 (JavaEE7) からは仕様が変わります
