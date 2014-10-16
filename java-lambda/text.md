# Java 8 - Lambda / Stream API #

はじめに

## ラムダに関連する文法拡張 ##

Java 8 では Java 言語に対していくつかの文法拡張がなされました。ここでは
Lambda (ラムダ) に関連する文法拡張について見ていきます。

### ラムダ記法 ###

Java 言語でラムダ式を書けるようになりました。新たに次のような式が書ける
ようになりました。

    (int x) -> { x + 1 }

引数 x に 1 を足すという処理を表したラムダ式です。

    (int x) -> { x + 1 }
    ^^^^^^^    ^^^^^^^^^
    引数部      処理本体

ラムダ式は引数部と処理本体に分かれており、それらを -> で繋ぐという構文
です。引数の数や処理本体の文の数に応じていくつかの略記が可能となってい
ます。


### 関数型インタフェース ###

文法の拡張というわけではなく、概念として追加されています。抽象メソッド
をひとつだけ持つインタフェースを、関数型インタフェースと呼びます。イン
タフェースの定義に FunctionalInterface アノテーションを付加することで、
関数型インタフェースであることを明示できるようになっています。

ラムダ式と後述するメソッド参照は、すべて関数型インタフェースの変数とし
て利用できます。


### メソッド参照 ###

関数型インタフェースの変数に、メソッドそのものを代入することができるよ
うになりました。

    private void onSubmitButtonActionPerformed(ActionEvent e) {
        ...
    }

    submitButton.addActionListener(this::onSubmitButtonActionPerformed);

厳密には「メソッドそのもの」ではなく「メソッドを呼び出すラムダ式」を表
現するのが、メソッド参照です。

インスタンスメソッド、クラスメソッド、コンストラクタのいずれもメソッド
参照として利用できます。

 * インスタンスメソッド
    * インスタンス名::メソッド名
    * クラス名::メソッド名
 * クラスメソッド
    * クラス名::メソッド名
 * コンストラクタ
    * クラス名::new

という文法です。

インスタンスメソッドへのメソッド参照を表す「クラス名::メソッド名」につ
いては、同じ名前のクラスメソッド (例: Integer::toString) がある場合、あ
いまいであるとしてコンパイルエラーとなります。

インスタンスメソッドへのメソッド参照は、

 * 第一引数はメソッドのレシーバー
 * 第二引数以降はメソッドの引数
 * 戻り値はメソッドの戻り値

というシグネチャを持つ関数型インタフェースに適合します。例えば Object
クラスの equals メソッドなら、

    BiFunction<Object, Object, Boolean> fn = Object::equals;

といった具合で、レシーバーの Object と比較対象の Object を引数にとり
Boolean を返す関数型インタフェースの変数になります。


### デフォルトメソッド ###

interface にメソッドのデフォルト実装を定義できるようになりました。List
や Map など、既存 API で定義されていた interface にラムダを利用したメソッ
ドを追加しつつ、アプリケーションプログラムのコンパイルエラーを回避する
ためです。

この言語拡張を利用して、List や Map といった既存の API に、ラムダを用い
たメソッドが追加されています。

    public interface List<E> extends Collection<E> {
        ...

        default void replaceAll(UnaryOperator<E> operator) {
            Objects.requireNonNull(operator);
            final ListIterator<E> li = this.listIterator();
            while (li.hasNext()) {
                li.set(operator.apply(li.next()));
            }
        }

        ...
    }

複数の interface を実装して、デフォルトメソッドが衝突した場合のコンパイ
ル結果をまとめました。

<table>
  <thead>
    <tr>
      <th>#</th>
      <th>インタフェース1</th>
      <th>インタフェース2</th>
      <th>実装クラス</th>
      <th>結果</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>1</td>
      <td>非デフォルトメソッド method1 を定義</td>
      <td>非デフォルトメソッド method1 を定義</td>
      <td>method1 を実装</td>
      <td>コンパイル可能 (Java 7 以前と同様)</td>
    </tr>
    <tr>
      <td>2</td>
      <td>デフォルトメソッド method1 を定義</td>
      <td>非デフォルトメソッド method1 を定義</td>
      <td>method1 を実装</td>
      <td>コンパイル可能</td>
    </tr>
    <tr>
      <td>3</td>
      <td>デフォルトメソッド method1 を定義</td>
      <td>非デフォルトメソッド method1 を定義</td>
      <td>method1 を実装しない</td>
      <td>インタフェース2の method1 が実装されていないものとしてコンパイルエラー</td>
    </tr>
    <tr>
      <td>4</td>
      <td>デフォルトメソッド method1 を定義</td>
      <td>デフォルトメソッド method1 を定義</td>
      <td>method1 を実装しない</td>
      <td>2つのインタフェースから関連しないデフォルトメソッドを継承しているとしてコンパイルエラー</td>
    </tr>
    <tr>
      <td>5</td>
      <td>デフォルトメソッド method1 を定義</td>
      <td>デフォルトメソッド method1 を定義</td>
      <td>method1 を実装</td>
      <td>コンパイル可能</td>
    </tr>
  </tbody>
</table>

多重継承によってコンパイルエラーになるケースで、片方のデフォルトメソッ
ドの実装を利用したい場合には、super キーワードを利用することでコンパイ
ルエラーを回避できます。

    public static interface IF1 {
        public default int method(int x) { return x + 1; }
    }

    public static interface IF2 {
        public default int method(int y) { return y + 2; }
    }

    public void useDefaultMethod() {
        class Impl implements IF1, IF2 {
            public int method(int y) { return IF2.super.method(y); }
        }

        System.out.println("impl.method(1): " + new Impl().method(1));  // 3
    }

デフォルトメソッドの定義は interface のクラスファイル内に展開されるよう
です。

    $ javap -p -c Tutor4\$IF2
    Compiled from "Tutor4.java"
    public interface Tutor4$IF2 {
      public int method(int);
        Code:
           0: iload_1
           1: iconst_2
           2: iadd
           3: ireturn
    }

ラムダには直接関係ありませんが、interface に対するもうひとつの拡張とし
て、interface にクラスメソッドを定義できるようになりました。

    @FunctionalInterface
    public interface Comparator<T> {
        ...

        public static <T, U extends Comparable<? super U>> Comparator<T> comparing(
                Function<? super T, ? extends U> keyExtractor)
        {
            Objects.requireNonNull(keyExtractor);
            return (Comparator<T> & Serializable)
                (c1, c2) -> keyExtractor.apply(c1).compareTo(keyExtractor.apply(c2));
        }

        ...
    }


## ラムダの基本 ##

### 無名内部クラス vs ラムダ式 ###

ラムダが追加される前 Java 7 以前では、いわゆるラムダ的なことを表現する
際には無名内部クラスという機能を使っていました:

    button.addActionListener(new ActionListener() {
        @Override
        public void actionPerformed(ActionEvent e) {
            System.out.println("on button clicked!");
        }
    });

入力の負担は IDE の自動補完によって軽減されたりもしますが、やりたいこと
に対するコード量がどうしても増えてしまう傾向があります。

上の例をラムダ式を使って書きなおしてみます:

    button.addActionListener((ActionEvent e) -> {
        System.out.println("on button clicked");
    });

もう少し削ってみます。

    button.addActionListener(e -> {
        System.out.println("on button clicked");
    });

仮引数の型 (例では ActionEvent) はコンパイラが推論してくれるようになっ
ているので、ほとんどの場合は省略可能です。また、今回の例ではラムダの引
数は 1 つなので、仮引数部分のカッコも省略可能です。

    button.addActionListener(e -> System.out.println("on button clicked"));

ラムダ式内部の処理が 1 文の場合、ブレースとセミコロンも省略可能です。

変わった点を列挙すると:

 * new ActionListener が消えた
 * @Override が消えた
 * public void actionPerformed が消えた
 * 引数 e の型宣言 (ActionEvent) が消えた
 * メソッド実装部分のブレースが消えた
 * メソッド実装部分の文末のセミコロンが消えた

といった具合です。無名内部クラスを使っていたコードに比べると、コード量
がぐっと減りました。

ボタンを押下したときの処理をメソッド化している場合を考えてみます。
Java 7 以前ではやはり無名内部クラスを利用する必要があり:

    button.addActionListener(new ActionListener() {
        @Override
        public void actionPerformed(ActionEvent e) {
            onButtonActionPerformed(e);
        }
    });

    private void onButtonActionPerformed(ActionEvent e) {
       System.out.println("on button clicked");
    }

というコードを書く必要がありました。
Java 8 以降では、もちろんラムダ式を使うこともできますが:

    button.addActionListener(e -> onButtonActionPerformed(e));

    private void onButtonActionPerformed(ActionEvent e) {
        System.out.println("on button clicked");
    }

メソッド参照を使うことで次のような書き方も可能です:

    button.addActionListener(this::onButtonActionPerformed);

    private void onButtonActionPerformed(ActionEvent e) {
        System.out.println("on button clicked");
    }


### ラムダ式の型 - 関数型インタフェース ###

Java 言語におけるラムダ式とは何か？その答えは「関数型インタフェースの型
を持つオブジェクト」です。

関数型インタフェースとは、抽象メソッドをひとつだけ持つインタフェースの
ことを指します。例えば run メソッドだけを抽象メソッドとして持つ
java.lang.Runnable インタフェースや、compare メソッドだけを抽象メソッド
として持つ java.util.Comparator インタフェースなどがこれに該当します。

コード中に現れるラムダ式が、どの関数型インタフェースの型を持つオブジェ
クトとして解釈されるかは、文脈に応じて変わります。

    // このアノテーションをつけることで、関数型インタフェースであることを
    // 明示できます。メソッドを追加したりすることでインタフェースが関数型
    // インタフェースの条件を満たさなくなると、コンパイルエラーが出ます。
    @FunctionalInterface
    public interface IntFunc<T> {
        public T apply(int n);
    }

    @FunctionalInterface
    public interface IntOp {
        public int apply(int n);
    }

    public static <T> T method1(IntFunc<T> fn, int x) {
        return fn.apply(x);
    }

    public static int method2(IntOp op, int x) {
        return op.apply(x);
    }

    int x = 1;
    method1(n -> n + 1, x);  // 1
    method2(n -> n + 1, x);  // 2

1, 2 で記述しているラムダ式は同じ字面ですが、全くの別物です。前者は
IntFunc インタフェースの、後者は IntOp インタフェースの型を持つオブジェ
クトとして解釈されます。

ラムダ式はあくまでも関数型インタフェースを型に持つオブジェクトなので、
他の型のオブジェクトと同様に変数に持つことができます:

    IntFunc<Integer> fn1 = n -> n + 1;
    IntOp fn2 = n -> n + 1;

ラムダ式をどの型を持つオブジェクトとして解釈するかは、変数の型によって
決められます。

また、ラムダ式の呼び出しはあくまでも関数型インタフェースのメソッド呼び
出しに過ぎません。リフレクションによるメソッド呼び出し (Method#invoke)
のような無駄なオーバーヘッドはありません。


### 汎用的な関数型インタフェース - java.util.function ###

関数型インタフェースの例として Runnable や Comparator を挙げてきました。
Java 7 以前の API では、こういった具合に用途に応じたインタフェースが用
意されてきましたが、Java 8 では汎用的な関数型インタフェースが用意されま
した。新たに追加された java.util.function パッケージに定義されています。

汎用的な関数型インタフェースは、大きく分けて 4 種類あります:

 * Function&lt;T, R&gt; (T を受け、R を返す)
 * Consumer&lt;T&gt; (T を受け、戻り値なし)
 * Predicate&lt;T&gt; (T を受け、boolean を返す)
 * Supplier&lt;R&gt; (引数を受けず、R を返す)

もう少し用途を特化させ、引数と戻り値の型が同じ関数型インタフェースとし
て:

 * UnaryOperator&lt;T&gt; (T を受け、T を返す)

があります。

さらにそれぞれのインタフェースにはいくつかのバリエーションがあり、
引数を 2 つ受け付けるものが用意されています:

 * BiFunction&lt;T, U, R&gt; (T, U を受け、R を返す)
 * BiConsumer&lt;T, U&gt; (T, U を受け、戻り値なし)
 * BiPredicate&lt;T, U&gt; (T, U を受け、boolean を返す)
 * BinaryOperator&lt;T&gt; (T を 2 つ受け、T を返す)

さらにさらに、プリミティブ型に特化したバリエーションのインタフェースが
用意されています。

 * IntFunction&lt;R&gt; (int を受け、R を返す)
 * IntConsumer (int を受け、戻り値なし)
 * IntPredicate (int を受け、boolean を返す)
 * IntSupplier (引数を受けず、int を返す)
 * IntUnaryOperator (int を受け、int を返す)
 * IntBinaryOperator (int を 2 つ受け、int を返す)

さらにさらにさらに、参照型からプリミティブ型に変換したり、参照型とプリ
ミティブ型を同時に受けたりすることに特化したインタフェースも用意されて
います:

 * ObjIntConsumer&lt;T&gt; (T と int を受け、戻り値なし)
 * ToIntFunction&lt;T&gt; (T を受け、int を返す)
 * ToIntBiFunction&lt;T, U&gt; (T と U を受け、int を返す)

こんなインタフェースが long, double, boolean (Supplier だけ) 向けにも
用意されています。他のプリミティブ型については諦めたようです。


## Optional ##

Java 8 では java.util.Optional というクラスが追加されました。Optional
は null になりうる値をラップするクラスです。null になりうる箇所を
Optional とすることで、null チェックの必要性を明示し、安全なプログラム
を書けるようにする仕組みです。

foo から bar を get し、その bar から baz を get し、その baz から
value を get するプログラムを考えてみます。いずれも null になりうる可能
性があるものとします。

    Foo foo = getFoo();
    if (foo == null)
        return null;

    Bar bar = foo.getBar();
    if (bar == null)
        return null;

    Baz baz = bar.getBaz();
    if (baz == null)
        return null;

    return baz.getValue();

getter の戻り値それぞれに対して null チェックが必要ですので、大体こんな
プログラムを書いていました。

    Optional<Foo> foo = Optional.ofNullable(getFoo());
    if (!foo.isPresent())
        return null;

    Optional<Bar> bar = Optional.ofNullable(foo.get().getBar());
    if (!bar.isPresent())
        return null;

    Optional<Baz> baz = Optional.ofNullable(bar.get().getBaz());
    if (!baz.isPresent())
        return null;

    return baz.getValue().orElse(null);

各 getter の戻り値を Optional でラップすることで、それが null を取りう
る値であるということを明示しています。値が null かどうかは
Optinoal.isPresent で調べることが可能です。Optional にラップされている
値は get で取得可能です。

Optional とラムダを組み合わせることで、より簡潔に書くことができます。

    return getFoo().map(foo -> foo.getBar())
                   .map(bar -> bar.getBaz())
                   .map(baz -> baz.getValue())
                   .orElse(null);

Optional.map は Function インタフェースを受け付けます。Optional が値を
保持していればその値を適用させ、null の場合はスルーします。null チェッ
クの連鎖を map メソッドのチェインで表現しています。

Optional.map は次のように実装されています:

    public<U> Optional<U> map(Function<? super T, ? extends U> mapper) {
        Objects.requireNonNull(mapper);
        if (!isPresent())
            return empty();
        else {
            return Optional.ofNullable(mapper.apply(value));
        }
    }

なお、Optional 変数自体に null を代入することは依然として可能です:

    Optional<String> s = null;
    s.isPresent();  // NullPointerException

Java 言語の機能でこういった事態を回避することは今のところ不可能であり、
null を代入することがないよう、プログラマが注意する必要があります。


## Stream API ##

ラムダのよくある用法として、リストに対する操作を、制御構文を使わず簡潔
に書けるというものがあります。例えば Java のこんなコードが:

    int sum = 0;
    for (Widget w : widgets) {
        if (w.getColor() == RED) {
            sum += w.getWeight();
        }
    }

Common Lisp ではこんな風に書けます:

    (reduce (lambda (sum w) (+ sum (get-weight w)))
            (remove-if-not (lambda (w) (= (get-color w) RED))
                           widgets)
            :initial-value 0)

といった具合のものです。当然 Java でもラムダを使うことで、この程度のラ
ムダ式の応用は可能になりました。

上の Java と Lisp のプログラムの大きな違いとして、Lisp のプログラムでは
中間リストが生成されているという点があります。 `remove-if-not` 関数の戻
り値としてリストが 1 つ生成されています。リストのサイズ次第では、無視で
きないほどのオーバーヘッドになりえます。

こうした問題への対応としては、多くの場合は遅延リストが利用されます。
Java 8 では Stream API としてその枠が設けられました。

Lisp のプログラムを Java のラムダと Stream を使って翻訳すると:

    widgets.stream()
           .filter(w -> w.getColor() == RED)
           .collect(Collectors.summingInt(w -> w.getWeight()));

といった具合になります。


### Stream API を使ってみる ###

Java 7 以前のプログラムを Stream API を使って書きなおしてみます。

 * 社員のリストから
 * 西暦 2000 年以前に入社した社員を抽出し
 * 社員を部署コードごとに分類し
 * 各部署の管理者が社員の評価を実施する

というプログラムを考えてみます。

    List<Employee> employees = getEmployees();
    Map<Department, List<Employee>> dep2emps = new HashMap<>();

    for (Employees emp : employees) {
        if (!emp.isJoinedBefore(2000)) {
            continue;
        }

        List<Employee> emps = dep2emps.get(emp.getDepartment());
        if (emps == null) {
            emps = new ArrayList<>();
            dep2emps.put(emp.getDepartment(), emps);
        }
        emps.add(emp);
    }

    for (Map.Entry<Department, List<Employee>> e : dep2emps.entrySet()) {
        Department dep = e.getKey();
        List<Employee> emps = e.getValue();
        dep.getManager().rating(emps);
    }

なんだかよく見るプログラムです。

これを Stream API を使って書きなおしてみます:

    List<Employee> employees = getEmployees();
    employees.stream()
             .filter(e -> e.isJoinedBefore(2000))
             .collect(Collectors.groupingBy(Employee::getDepartment()))
             .forEach((dep, emps) -> dep.getManager().rating(emps));

スッキリしました。

元のコードで冗長だった (そしてなんとも Java っぽい) 「Map から List を
get し null チェックして、null なら new して put する」部分は、
Collectors.groupingBy の中に押し込められました。

Map.entrySet でループする箇所も、forEach を利用することで、長ったらしい
Map.Entry の型宣言を省くことができます。

何より、最初の箇条書きをそっくりそのままプログラムに落とし込んだような
コードになっている点が素晴らしいですね。


### 中間操作 ###

Stream の操作は大きく中間操作と終端操作に分けられます。Stream 操作のパ
イプラインは 0 個以上の中間操作と、1 つの終端操作から成り立ちます。

中間操作は Stream から Stream を生成する操作です。中間操作は即座に評価
されることはなく、常に遅延されます。例えば中間操作である map メソッドを
呼び出しても、即座に値のマッピングが行われることはなく、その後に続く終
端操作によって Stream をトラバースする際にマッピングが行われます。

    Stream.of("Dog", "Cat", "Dog", "Monkey", "Dog");
          .peek(s -> System.out.println("Before distinct: " + s))  // 中間操作
          .distinct()
          .forEach(s -> System.out.println("After distinct: " + s));  // 終端操作

実行結果は

    Before distinct: Dog
    After distinct: Dog
    Before distinct: Cat
    After distinct: Cat
    Before distinct: Dog
    Before distinct: Monkey
    After distinct: Monkey
    Before distinct: Dog

となります。Before と After が交互に出力されており、distinct の前の
peek に渡したラムダの実行が最後の forEach の実行まで遅延されていることが
分かります。


### 終端操作 ###

終端操作は Stream をトラバースして結果や副作用を生成する操作です。
Stream.forEach や IntStream.sum などが該当します。終端操作が完了すると
Stream は消費済みとみなされ、以降は使用できなくなります。

    Stream<String> stream = Stream.of("hero", "dog", "monkey", "bird");
    List<String> legend = stream.map(String::toUpperCase).collect(Collectors.toList());
    System.out.println(legend);

    // stream は終端操作である collect を通過しているので、
    // 再度使おうとすると IllegalStateException が発生する
    List<String> legend2 = stream.map(String::toLowerCase).collect(Collectors.toList());
    System.out.println(legend2);

実行結果:

    [HERO, DOG, MONKEY, BIRD]
    Exception in thread "main" java.lang.IllegalStateException: stream has already been operated upon or closed
            at java.util.stream.AbstractPipeline.<init>(AbstractPipeline.java:203)
            at java.util.stream.ReferencePipeline.<init>(ReferencePipeline.java:94)
            at java.util.stream.ReferencePipeline$StatelessOp.<init>(ReferencePipeline.java:618)
            at java.util.stream.ReferencePipeline$3.<init>(ReferencePipeline.java:187)
            at java.util.stream.ReferencePipeline.map(ReferencePipeline.java:186)
            at Tutor4.useTwice(Tutor4.java:219)
            at Tutor4.main(Tutor4.java:234)

toUpperCase でマップして得た List は出力されていますが、その後
toLowerCase でマップしようとしたところで例外が発生しています。


### 独自の中間操作 ###

Stream API を利用していると、あらかじめ用意されている中間操作、終端操作
では事足りず、独自の中間操作、終端操作を実装したくなるかもしれません。
Stream API では独自の中間操作、終端操作を実装するための手段が用意されて
います。

中間操作は「Stream から Stream を生成する」処理のことを指します。なので
独自の中間操作を実装したければ、端的に言えば Stream を受けて Stream を
生成すればよいということになります。

1 つ例として「2 つの Stream から取り出した要素を関数に適用しつつ 1 つの
Stream にまとめる」という中間操作を考えてみます。

    public static <T, U, R> Stream<R> zipWith(Stream<T> stream1, Stream<U> stream2, BiFunction<T, U, R> fn) {
        Iterator<T> i1 = stream1.iterator();
        Iterator<U> i2 = stream2.iterator();
        Iterator<R> iter = new Iterator<R>() {
            @Override
            public boolean hasNext() {
                return i1.hasNext() && i2.hasNext();
            }

            @Override
            public R next() {
                return fn.apply(i1.next(), i2.next());
            }
        };

        Spliterator<Integer> spliter = Spliterators.spliteratorUnknownSize(
                iter, Spliterator.NONNULL | Spliterator.ORDERED)
        return StreamSupport.stream(spliter, false);
    }

こんな感じで使います:

    Stream<Integer> ns1 = Stream.of(1, 2, 3, 4, 5);
    Stream<Integer> ns2 = Stream.of(5, 4, 3, 2, 1);
    zipWith(ns1, ns2, Math::max).forEach(System.out::println);

    処理結果:
    5
    4
    3
    4
    5

zipWith で Stream のインスタンスを得るまでの流れを追うと:

 1. ソースの Stream から Iterator を得る
 2. 1 をラップした Iterator を生成する
 3. 2 の Iterator から Spliterator を生成する
 4. 3 の Spliterator をソースとして Stream を生成する

という流れとなっています。この流れはもっとも基本的で単純な、Stream を構
築するまでの流れです。Javadoc によれば、Spliterator の実装を工夫するこ
とで、並列パフォーマンスの向上を狙うことができるようです。


## ラムダ/Stream をサポートする API ##

java.nio.file (Files.lines, walk ...)
java.util (Map.computeIfAbsent ...)
java.util.concurrent


## ラムダ式の評価 ##

ラムダ式の呼び出しはインタフェースのメソッドと同様であるということは前
述した通りです。では、ラムダ式そのものの評価 (= ラムダ式から関数型イン
タフェースのオブジェクトを得る処理) はどのように行われるのか？

その真相はラムダ式を伴う Java プログラムをコンパイルして生成されるクラ
スファイルを解析していくことで確認することができます。ここではこれにつ
いて触れていきます。


### ラムダ式のコンパイル結果 ###

さっそくですが、ラムダ式のコンパイル結果を見てます。

    $ cat UseLambda.java
    import java.util.function.*;

    public class UseLambda {
        public static void main(String[] args) {
            callItWith1(x -> x + 1);
        }

        private static int callItWith1(IntUnaryOperator op) {
            return op.applyAsInt(1);
        }
    }

    $ javap -c -p UseLambda
    Compiled from "UseLambda.java"
    public class UseLambda {
      public UseLambda();
        Code:
           0: aload_0
           1: invokespecial #1                  // Method java/lang/Object."<init>":()V
           4: return

      public static void main(java.lang.String[]);
        Code:
           0: invokedynamic #2,  0              // InvokeDynamic #0:applyAsInt:()Ljava/util/function/IntUnaryOperator;
           5: invokestatic  #3                  // Method callItWith1:(Ljava/util/function/IntUnaryOperator;)I
           8: pop
           9: return

      private static int callItWith1(java.util.function.IntUnaryOperator);
        Code:
           0: aload_0
           1: iconst_1
           2: invokeinterface #4,  2            // InterfaceMethod java/util/function/IntUnaryOperator.applyAsInt:(I)I
           7: ireturn

      private static int lambda$main$0(int);
        Code:
           0: iload_0
           1: iconst_1
           2: iadd
           3: ireturn
    }

ラムダ式は invokedynamic という命令にコンパイルされます。

ラムダ式内部の処理は、同クラスの lambda$main$0 というメソッドの中に展開
されています。ラムダ式が表す関数型インタフェースのオブジェクトに対する
メソッド呼び出し (この例では applyAsInt) が、巡り巡って lambda$main$0
にたどり着きます。

この関連付けを行うのが invokedynamic 命令です。


### invokedynamic ###

invokedynamicは Java 7 から追加された JVM の呼び出し命令です。Java 6 以
前は 4 つの呼び出し命令がありました:

 * invokestatic: 静的メソッドの呼び出し
 * invokevirtual: 動的ディスパッチを必要とするメソッド呼び出し
 * invokeinterface: メソッド・ディスパッチがインタフェースに基づいて実行される呼び出し命令
 * invokespecial: 上記以外のメソッド (コンストラクタ、private メソッドなど) の呼び出し命令

これらの呼び出し命令はコンパイル時に呼び出し先のメソッドが決定されます
が、invokedynamic は実行時に呼び出し先のメソッドが決定するという点が大
きく異なります。

![invokedynamic](invokedynamic.png)

invokedynamic によるメソッド呼び出しの流れは次の通りです:

 1. invokedynamic に関連付けられている bootstrap メソッドを呼び出す
 2. Bootstrap メソッドは CallSite オブジェクトを返す
 3. CallSite から呼び出し先の MethodHandle を得る
 4. MethodHandle を経由して、メソッドを呼び出す

bootstrap メソッドとは、invokedynamic に関連付けられる CallSite を構築
する処理が実装された static メソッドです。すべての invokedynamic 命令は
bootstrap メソッドへの参照を持っています。CallSite の構築と、
MethodHandle の初期値を CallSite に紐付けます。bootstrap メソッドの呼び
出しは、その invokedynamic 命令が初めて実行されるときにだけ行われます。

CallSite が返す MethodHandle は、常に同じものでも構いませんし、毎回違う
ものでも構いません。このように呼び出し先のメソッドが動的に変えられる点が、
他の 4 つの呼び出し命令と大きく異なります。


### LambdaMetafactory ###

前述した通り、ラムダ式は invokedynamic 命令にコンパイルされます。ラムダ
式の invokedynamic 命令には LambdaMetafactory クラスの metafactory メソッ
ドが bootstrap メソッドとして関連付けられます。

UseLambda に -v オプションをつけて javap してみます:

    $ javap -v -c -p UseLambda
    Classfile /home/kazuki/sources/writing/java-lambda/sandbox/UseLambda.class
      Last modified 2014/10/13; size 1018 bytes
      MD5 checksum 0ec5849decc1a5fda4ed01164d157016
      Compiled from "UseLambda.java"
    public class UseLambda
      minor version: 0
      major version: 52
      flags: ACC_PUBLIC, ACC_SUPER
    Constant pool:
       #1 = Methodref          #6.#19         // java/lang/Object."<init>":()V
       #2 = InvokeDynamic      #0:#24         // #0:applyAsInt:()Ljava/util/function/IntUnaryOperator;
       #3 = Methodref          #5.#25         // UseLambda.callItWith1:(Ljava/util/function/IntUnaryOperator;)I
       #4 = InterfaceMethodref #26.#27        // java/util/function/IntUnaryOperator.applyAsInt:(I)I
       #5 = Class              #28            // UseLambda
       #6 = Class              #29            // java/lang/Object
       #7 = Utf8               <init>
       #8 = Utf8               ()V
       #9 = Utf8               Code
      #10 = Utf8               LineNumberTable
      #11 = Utf8               main
      #12 = Utf8               ([Ljava/lang/String;)V
      #13 = Utf8               callItWith1
      #14 = Utf8               (Ljava/util/function/IntUnaryOperator;)I
      #15 = Utf8               lambda$main$0
      #16 = Utf8               (I)I
      #17 = Utf8               SourceFile
      #18 = Utf8               UseLambda.java
      #19 = NameAndType        #7:#8          // "<init>":()V
      #20 = Utf8               BootstrapMethods
      #21 = MethodHandle       #6:#30         // invokestatic java/lang/invoke/LambdaMetafactory.metafactory:(Ljava/lang/invoke/MethodHandles$Lookup;Ljava/lang/String;Ljava/lang/invoke/MethodType;Ljava/lang/invoke/MethodType;Ljava/lang/invoke/MethodHandle;Ljava/lang/invoke/MethodType;)Ljava/lang/invoke/CallSite;
      #22 = MethodType         #16            //  (I)I
      #23 = MethodHandle       #6:#31         // invokestatic UseLambda.lambda$main$0:(I)I
      #24 = NameAndType        #32:#33        // applyAsInt:()Ljava/util/function/IntUnaryOperator;
      #25 = NameAndType        #13:#14        // callItWith1:(Ljava/util/function/IntUnaryOperator;)I
      #26 = Class              #34            // java/util/function/IntUnaryOperator
      #27 = NameAndType        #32:#16        // applyAsInt:(I)I
      #28 = Utf8               UseLambda
      #29 = Utf8               java/lang/Object
      #30 = Methodref          #35.#36        // java/lang/invoke/LambdaMetafactory.metafactory:(Ljava/lang/invoke/MethodHandles$Lookup;Ljava/lang/String;Ljava/lang/invoke/MethodType;Ljava/lang/invoke/MethodType;Ljava/lang/invoke/MethodHandle;Ljava/lang/invoke/MethodType;)Ljava/lang/invoke/CallSite;
      #31 = Methodref          #5.#37         // UseLambda.lambda$main$0:(I)I
      #32 = Utf8               applyAsInt
      #33 = Utf8               ()Ljava/util/function/IntUnaryOperator;
      #34 = Utf8               java/util/function/IntUnaryOperator
      #35 = Class              #38            // java/lang/invoke/LambdaMetafactory
      #36 = NameAndType        #39:#43        // metafactory:(Ljava/lang/invoke/MethodHandles$Lookup;Ljava/lang/String;Ljava/lang/invoke/MethodType;Ljava/lang/invoke/MethodType;Ljava/lang/invoke/MethodHandle;Ljava/lang/invoke/MethodType;)Ljava/lang/invoke/CallSite;
      #37 = NameAndType        #15:#16        // lambda$main$0:(I)I
      #38 = Utf8               java/lang/invoke/LambdaMetafactory
      #39 = Utf8               metafactory
      #40 = Class              #45            // java/lang/invoke/MethodHandles$Lookup
      #41 = Utf8               Lookup
      #42 = Utf8               InnerClasses
      #43 = Utf8               (Ljava/lang/invoke/MethodHandles$Lookup;Ljava/lang/String;Ljava/lang/invoke/MethodType;Ljava/lang/invoke/MethodType;Ljava/lang/invoke/MethodHandle;Ljava/lang/invoke/MethodType;)Ljava/lang/invoke/CallSite;
      #44 = Class              #46            // java/lang/invoke/MethodHandles
      #45 = Utf8               java/lang/invoke/MethodHandles$Lookup
      #46 = Utf8               java/lang/invoke/MethodHandles
    {
      public UseLambda();
        descriptor: ()V
        flags: ACC_PUBLIC
        Code:
          stack=1, locals=1, args_size=1
             0: aload_0
             1: invokespecial #1                  // Method java/lang/Object."<init>":()V
             4: return
          LineNumberTable:
            line 3: 0

      public static void main(java.lang.String[]);
        descriptor: ([Ljava/lang/String;)V
        flags: ACC_PUBLIC, ACC_STATIC
        Code:
          stack=1, locals=1, args_size=1
             0: invokedynamic #2,  0              // InvokeDynamic #0:applyAsInt:()Ljava/util/function/IntUnaryOperator;
             5: invokestatic  #3                  // Method callItWith1:(Ljava/util/function/IntUnaryOperator;)I
             8: pop
             9: return
          LineNumberTable:
            line 5: 0
            line 6: 9

      private static int callItWith1(java.util.function.IntUnaryOperator);
        descriptor: (Ljava/util/function/IntUnaryOperator;)I
        flags: ACC_PRIVATE, ACC_STATIC
        Code:
          stack=2, locals=1, args_size=1
             0: aload_0
             1: iconst_1
             2: invokeinterface #4,  2            // InterfaceMethod java/util/function/IntUnaryOperator.applyAsInt:(I)I
             7: ireturn
          LineNumberTable:
            line 9: 0

      private static int lambda$main$0(int);
        descriptor: (I)I
        flags: ACC_PRIVATE, ACC_STATIC, ACC_SYNTHETIC
        Code:
          stack=2, locals=1, args_size=1
             0: iload_0
             1: iconst_1
             2: iadd
             3: ireturn
          LineNumberTable:
            line 5: 0
    }
    SourceFile: "UseLambda.java"
    InnerClasses:
         public static final #41= #40 of #44; //Lookup=class java/lang/invoke/MethodHandles$Lookup of class java/lang/invoke/MethodHandles
    BootstrapMethods:
      0: #21 invokestatic java/lang/invoke/LambdaMetafactory.metafactory:(Ljava/lang/invoke/MethodHandles$Lookup;Ljava/lang/String;Ljava/lang/invoke/MethodType;Ljava/lang/invoke/MethodType;Ljava/lang/invoke/MethodHandle;Ljava/lang/invoke/MethodType;)Ljava/lang/invoke/CallSite;
        Method arguments:
          #22 (I)I
          #23 invokestatic UseLambda.lambda$main$0:(I)I
          #22 (I)I

がんばって追ってみれば、ラムダ式の invokedynamic 命令に
LambdaMetafactory の metafactory メソッドに対する invokestatic が関連付
けられていることが分かります。

metafactory メソッド内では、

 * ラムダ式の実体となるオブジェクトの生成戦略を決定
 * lambda$main$0 メソッドを呼び出すプロキシクラスの生成
 * アダプタクラスのメソッドを呼び出す MethodHandle を生成

といったことを行います。

プロキシクラスが、ラムダ式の実体となるオブジェクトであると言えます。ラ
ムダ式が表す関数型インタフェースを実装したクラスです。プロキシクラスが
実装したメソッドから、ラムダ式の処理の実体 (lambda$main$0 メソッドなど)
が呼び出されます。

少し追いかけてみます:

    public class LambdaMetafactory {
        ...

        public static CallSite metafactory(MethodHandles.Lookup caller,
                                           String invokedName,
                                           MethodType invokedType,
                                           MethodType samMethodType,
                                           MethodHandle implMethod,
                                           MethodType instantiatedMethodType)
                throws LambdaConversionException {
            AbstractValidatingLambdaMetafactory mf;
            mf = new InnerClassLambdaMetafactory(caller, invokedType,
                                                 invokedName, samMethodType,
                                                 implMethod, instantiatedMethodType,
                                                 false, EMPTY_CLASS_ARRAY, EMPTY_MT_ARRAY);
            mf.validateMetafactoryArgs();
            return mf.buildCallSite();
        }

        ...
    }

InnerClassLambdaMetafactory の buildCallSite メソッドの戻り値を返してい
ます。

invokedType は CallSite の期待されるシグネチャを表します。これはラムダ
式が実装する関数型インタフェースのシグネチャ**ではなく**、ラムダ式によっ
て表現されるオブジェクトを得るために呼び出されるメソッドのシグネチャで
す。

InnerClassLambdaMetafactory を追ってみます。

    /* package */ final class InnerClassLambdaMetafactory extends AbstractValidatingLambdaMetafactory {
        ...
        private static final String NAME_FACTORY = "get$Lambda";
        ...

        @Override
        CallSite buildCallSite() throws LambdaConversionException {
            final Class<?> innerClass = spinInnerClass();
            if (invokedType.parameterCount() == 0) {
                final Constructor[] ctrs = AccessController.doPrivileged(
                        new PrivilegedAction<Constructor[]>() {
                    @Override
                    public Constructor[] run() {
                        Constructor<?>[] ctrs = innerClass.getDeclaredConstructors();
                        if (ctrs.length == 1) {
                            // The lambda implementing inner class constructor is private, set
                            // it accessible (by us) before creating the constant sole instance
                            ctrs[0].setAccessible(true);
                        }
                        return ctrs;
                    }
                        });
                if (ctrs.length != 1) {
                    throw new LambdaConversionException("Expected one lambda constructor for "
                            + innerClass.getCanonicalName() + ", got " + ctrs.length);
                }

                try {
                    Object inst = ctrs[0].newInstance();
                    return new ConstantCallSite(MethodHandles.constant(samBase, inst));
                }
                catch (ReflectiveOperationException e) {
                    throw new LambdaConversionException("Exception instantiating lambda object", e);
                }
            } else {
                try {
                    UNSAFE.ensureClassInitialized(innerClass);
                    return new ConstantCallSite(
                            MethodHandles.Lookup.IMPL_LOOKUP
                                 .findStatic(innerClass, NAME_FACTORY, invokedType));
                }
                catch (ReflectiveOperationException e) {
                    throw new LambdaConversionException("Exception finding constructor", e);
                }
            }
        }

        ...
    }

spinInnerClass メソッドの呼び出しにより、プロキシクラスを呼び出し元の内
部クラスとして生成しています。

invokedType によって表現されるメソッドシグネチャのパラメータ数により、
生成する CallSite とその初期値となる MethodHandle を切り替えています。
invokedType によって表現されるメソッドの引数は、ラムダ式がキャプチャす
る変数、すなわちラムダ式の内部からアクセスされる外側の変数です。

    void method() {
        callWithIt1(x -> x + 1);  // (1)
        int y = 1;
        callWithIt1(x -> x + y);  // (2)
    }

(1) のラムダ式は、式の引数だけを用いた式であり、キャプチャする変数はあ
りません。(2) のラムダ式は、式の外部で定義された変数 y を用いており、y
を式内にキャプチャしているといえます。

(1) のようなラムダ式であれば invokedType のパラメータ数は 0 となり、
(2) のようなラムダ式であれば invokedType のパラメータ数は 1 となります。

まず、キャプチャする変数がない場合に生成している CallSite を見てみます:

    try {
        Object inst = ctrs[0].newInstance();
        return new ConstantCallSite(MethodHandles.constant(samBase, inst));
    }
    catch (ReflectiveOperationException e) {
        throw new LambdaConversionException("Exception instantiating lambda object", e);
    }

ここで生成している CallSite が持つメソッドハンドルは、
MethodHandles.constant が返すメソッドハンドルです。
MethodHandles.constant は、オブジェクトとその型を引数に取り、そのオブジェ
クトをそっくりそのまま返すメソッドハンドルを返すファクトリメソッドです。
つまりこの CallSite から返される MethodHandle を呼び出すと、 samBase 型
であるオブジェクト inst が返ってきます。

次にキャプチャする変数がある場合に生成している CallSite を見てみます:

    private static final String NAME_FACTORY = "get$Lambda";
    ...

    try {
        UNSAFE.ensureClassInitialized(innerClass);
        return new ConstantCallSite(
                MethodHandles.Lookup.IMPL_LOOKUP
                     .findStatic(innerClass, NAME_FACTORY, invokedType));
    }
    catch (ReflectiveOperationException e) {
        throw new LambdaConversionException("Exception finding constructor", e);
    }

ここで生成している CallSite が持つメソッドハンドルは、innerClass の
static メソッドである get$Lambda への参照です。そのシグネチャは
invokedType で表現されるシグネチャ、つまりキャプチャする変数を引数に取
り、プロキシクラスのインスタンスを返すメソッドです。

いずれも場合であっても CallSite が返すメソッドハンドルを呼び出すと、プ
ロキシクラスのインスタンスが返ってきます。ただしそのオブジェクトの生成
戦略はラムダ式内に変数をキャプチャするかどうかで切り替わり、変数をキャ
プチャする必要がなければ、あらかじめインスタンス化されたオブジェクトが、
変数をキャプチャする必要があれば呼び出しのたびに新しいオブジェクトが生
成されます。

つまり、ラムダ式によって表現される関数型インタフェースのオブジェクトの
実体は、metafactory メソッド内で実行時に生成されるプロキシクラスのイン
スタンスであると言えます。


### プロキシクラス ###

ラムダ式の invokedynamic 命令には LambdaMetafactory の metafactory メソッ
ドが bootstrap メソッドとして関連付けられます。metafactory メソッドでは、
ラムダ式に対応するプロキシクラスが生成されます。ラムダ式により表現され
る関数型インタフェースのオブジェクトの実体は、このプロキシクラスのイン
スタンスとなります。

実際どのようなプロキシクラスが生成されているのか、確認することができま
す。

    $ cat UseLambda.java
    import java.util.function.*;

    public class UseLambda {
        public static void main(String[] args) {
            callItWith1(x -> x + 1);
            int y = 1;
            callItWith1(x -> x + y);
        }

        private static int callItWith1(IntUnaryOperator op) {
            return op.applyAsInt(1);
        }
    }

    $ java -Djdk.internal.lambda.dumpProxyClasses=lambdaproxy UseLambda
    $ ls lambdaproxy
    UseLambda$$Lambda$1.class  UseLambda$$Lambda$2.class

    $ cd lambdaproxy
    $ javap -c -p UseLambda\$\$Lambda\$1
    final class UseLambda$$Lambda$1 implements java.util.function.IntUnaryOperator {
      private UseLambda$$Lambda$1();
        Code:
           0: aload_0
           1: invokespecial #10                 // Method java/lang/Object."<init>":()V
           4: return

      public int applyAsInt(int);
        Code:
           0: iload_1
           1: invokestatic  #17                 // Method UseLambda.lambda$main$0:(I)I
           4: ireturn
    }

    $ javap -c -p UseLambda\$\$Lambda\$2
    final class UseLambda$$Lambda$2 implements java.util.function.IntUnaryOperator {
      private final int arg$1;

      private UseLambda$$Lambda$2(int);
        Code:
           0: aload_0
           1: invokespecial #13                 // Method java/lang/Object."<init>":()V
           4: aload_0
           5: iload_1
           6: putfield      #15                 // Field arg$1:I
           9: return

      private static java.util.function.IntUnaryOperator get$Lambda(int);
        Code:
           0: new           #2                  // class UseLambda$$Lambda$2
           3: dup
           4: iload_0
           5: invokespecial #19                 // Method "<init>":(I)V
           8: areturn

      public int applyAsInt(int);
        Code:
           0: aload_0
           1: getfield      #15                 // Field arg$1:I
           4: iload_1
           5: invokestatic  #27                 // Method UseLambda.lambda$main$1:(II)I
           8: ireturn
    }

システムプロパティ jdk.internal.lambda.dumpProxyClasses にフォルダ名を
指定して実行すると、実行時に生成するプロキシクラスをフォルダ内にダンプ
するようになっています。

x -> x + 1 に対応するプロキシクラスが UseLambda$$Lambda$1 クラスで、x
-> x + y に対応するプロキシクラスが UseLambda$$Lambda$2 クラスです。

キャプチャする変数がない UseLambda$$Lambda$1 には get$Lambda メソッドが
ないことを確認できます。同クラスはラムダ式の関数型インタフェースである
IntUnaryOperator を実装し、applyAsInt メソッドでは
UseLambda.lambda$main$0 を呼び出していることが分かります。

キャプチャする変数がある UseLambda$$Lambda$2 には get$Lambda メソッドが
あることを確認できます。ラムダ式では、外部で定義されている int 変数 y
をキャプチャしているので、get$Lambda メソッドの引数として int を 1 つ受
けています。get$Lambda メソッドでは UseLambda$$Lambda$2 を new していま
す。キャプチャする変数を保持しておくためのインスタンスフィールド arg$1
も確認できます。
