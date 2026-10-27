-- 自作の動作確認用教材。原本やユーザーの学習履歴は含めない。
-- 同じIDが存在する場合はスキップし、編集済みデータを上書きしない。
BEGIN;

-- subjects
INSERT INTO public.subjects (id, name) VALUES ('11111111-1111-4111-8111-111111111111', '数学') ON CONFLICT DO NOTHING;

-- exams
INSERT INTO public.exams (id, name, category, subject_id) VALUES ('22222222-2222-4222-8222-222222222222', '東北大学工学部編入・数学', '編入学', '11111111-1111-4111-8111-111111111111') ON CONFLICT DO NOTHING;

-- genres
INSERT INTO public.genres (id, subject_id, name, description_md) VALUES ('33333333-3333-4333-8333-333333333333', '11111111-1111-4111-8111-111111111111', '線形代数', 'ベクトルと行列、固有値、固有ベクトル、対角化、行列の累乗を扱う。画面と学習フローの確認用に用意した定義。') ON CONFLICT DO NOTHING;

-- formats
INSERT INTO public.formats (id, name, structure, answer_type, description_md) VALUES ('44444444-4444-4444-8444-444444444444', '複数小問・計算中心', '複数小問', '計算', '一つの大問に複数の計算小問を含む。動作確認用の分類であり、対象試験の実際の出題傾向を確定したものではない。') ON CONFLICT DO NOTHING;

-- knowledge_elements
INSERT INTO public.knowledge_elements (id, genre_id, title, body_md, cost) VALUES ('55555555-5555-4555-8555-555555555551', '33333333-3333-4333-8333-333333333333', '固有値', '# 固有値
正方行列 $A$ とゼロでないベクトル $v$ が $Av=\lambda v$ を満たすとき、$\lambda$ を固有値という。
$\det(A-\lambda I)=0$ を解いて求める。対応するベクトルは[固有ベクトル](/knowledge/55555555-5555-4555-8555-555555555552)を参照。
', NULL) ON CONFLICT DO NOTHING;
INSERT INTO public.knowledge_elements (id, genre_id, title, body_md, cost) VALUES ('55555555-5555-4555-8555-555555555552', '33333333-3333-4333-8333-333333333333', '固有ベクトル', '# 固有ベクトル
[固有値](/knowledge/55555555-5555-4555-8555-555555555551) $\lambda$ に対して $(A-\lambda I)v=0$ を満たすゼロでないベクトルが固有ベクトル。
非ゼロの定数倍も同じ固有値の固有ベクトルになる。単位ベクトルにするときは[正規化](/knowledge/55555555-5555-4555-8555-555555555553)を使う。
', NULL) ON CONFLICT DO NOTHING;
INSERT INTO public.knowledge_elements (id, genre_id, title, body_md, cost) VALUES ('55555555-5555-4555-8555-555555555553', '33333333-3333-4333-8333-333333333333', 'ベクトルの正規化', '# ベクトルの正規化
実数成分の非ゼロベクトル $v$ の長さは $\|v\|=\sqrt{\sum_i v_i^2}$。
$u=v/\|v\|$ とすると $\|u\|=1$。例えば $(1,1)^T$ は $(1,1)^T/\sqrt{2}$ に正規化できる。ゼロベクトルはこの方法では正規化できない。
', NULL) ON CONFLICT DO NOTHING;
INSERT INTO public.knowledge_elements (id, genre_id, title, body_md, cost) VALUES ('55555555-5555-4555-8555-555555555554', '33333333-3333-4333-8333-333333333333', '対角化', '# 対角化
一次独立な[固有ベクトル](/knowledge/55555555-5555-4555-8555-555555555552)を列に並べた正則行列 $P$ が取れるとき、$D=P^{-1}AP$ は対角行列になる。
対角成分は各列に対応する固有値。$A=PDP^{-1}$ と表せる。すべての正方行列が対角化できるわけではない。
', NULL) ON CONFLICT DO NOTHING;
INSERT INTO public.knowledge_elements (id, genre_id, title, body_md, cost) VALUES ('55555555-5555-4555-8555-555555555555', '33333333-3333-4333-8333-333333333333', '行列の累乗', '# 行列の累乗
[対角化](/knowledge/55555555-5555-4555-8555-555555555554)により $A=PDP^{-1}$ と表せるとき、正整数 $n$ に対して $A^n=PD^nP^{-1}$。
$D=\operatorname{diag}(\lambda_1,\lambda_2)$ なら $D^n=\operatorname{diag}(\lambda_1^n,\lambda_2^n)$。
', NULL) ON CONFLICT DO NOTHING;

-- exam_genres
INSERT INTO public.exam_genres (exam_id, genre_id) VALUES ('22222222-2222-4222-8222-222222222222', '33333333-3333-4333-8333-333333333333') ON CONFLICT DO NOTHING;

-- exam_formats
INSERT INTO public.exam_formats (exam_id, format_id) VALUES ('22222222-2222-4222-8222-222222222222', '44444444-4444-4444-8444-444444444444') ON CONFLICT DO NOTHING;

-- problems
INSERT INTO public.problems (id, exam_id, format_id, body_md, answer_md, explanation_md, retired_at) VALUES ('66666666-6666-4666-8666-666666666661', '22222222-2222-4222-8222-222222222222', '44444444-4444-4444-8444-444444444444', '# 動作確認用問題A：固有値と正規化
独自に作成した確認用問題です。
$$A=\begin{pmatrix}2&1\\1&2\end{pmatrix}$$
1. $A$ の固有値をすべて求めよ。
2. 各固有値に対応する固有ベクトルを一つずつ求めよ。
3. 求めた固有ベクトルをそれぞれ長さ1に正規化せよ。
', '固有値は $3,1$。
それぞれの固有ベクトルの一例は $(1,1)^T,(1,-1)^T$。
正規化した一例は $\frac{1}{\sqrt{2}}(1,1)^T,\frac{1}{\sqrt{2}}(1,-1)^T$。符号を反転したものも正解。
', '$\det(A-\lambda I)=(2-\lambda)^2-1=(\lambda-3)(\lambda-1)$。
$\lambda=3$ では $v_1=v_2$、$\lambda=1$ では $v_1=-v_2$。選んだベクトルの長さはどちらも $\sqrt{2}$ なので割って正規化する。
使用する知識：[固有値](/knowledge/55555555-5555-4555-8555-555555555551)、[固有ベクトル](/knowledge/55555555-5555-4555-8555-555555555552)、[正規化](/knowledge/55555555-5555-4555-8555-555555555553)。
', NULL) ON CONFLICT DO NOTHING;
INSERT INTO public.problems (id, exam_id, format_id, body_md, answer_md, explanation_md, retired_at) VALUES ('66666666-6666-4666-8666-666666666662', '22222222-2222-4222-8222-222222222222', '44444444-4444-4444-8444-444444444444', '# 動作確認用問題B：対角化
独自に作成した確認用問題です。
$$A=\begin{pmatrix}1&2\\0&3\end{pmatrix}$$
1. 固有値と、それぞれの固有値に対応する固有ベクトルを一つずつ求めよ。
2. 固有ベクトルを列に並べた行列 $P$ を作り、$P^{-1}$ を求めよ。
3. $P^{-1}AP$ を計算して対角行列になることを確認せよ。
', '固有値は $1,3$。対応する固有ベクトルの一例は $(1,0)^T,(1,1)^T$。
$$P=\begin{pmatrix}1&1\\0&1\end{pmatrix},\quad P^{-1}=\begin{pmatrix}1&-1\\0&1\end{pmatrix},\quad P^{-1}AP=\begin{pmatrix}1&0\\0&3\end{pmatrix}.$$
固有ベクトルの非ゼロ定数倍や列の順序変更も、対応する対角成分を合わせれば正解。
', '上三角行列なので固有値は対角成分の $1,3$。固有値1では第二成分が0、固有値3では二つの成分が等しい。
選んだ二つの固有ベクトルは一次独立なので $P$ は正則。行列積を計算すると対角成分が1と3になる。
使用する知識：[固有値](/knowledge/55555555-5555-4555-8555-555555555551)、[固有ベクトル](/knowledge/55555555-5555-4555-8555-555555555552)、[対角化](/knowledge/55555555-5555-4555-8555-555555555554)。
', NULL) ON CONFLICT DO NOTHING;
INSERT INTO public.problems (id, exam_id, format_id, body_md, answer_md, explanation_md, retired_at) VALUES ('66666666-6666-4666-8666-666666666663', '22222222-2222-4222-8222-222222222222', '44444444-4444-4444-8444-444444444444', '# 動作確認用問題C：行列の累乗
独自に作成した確認用問題です。
$$P=\begin{pmatrix}1&1\\0&1\end{pmatrix},\quad D=\begin{pmatrix}2&0\\0&4\end{pmatrix},\quad A=PDP^{-1}.$$
1. $P^{-1}$ と $A$ を求めよ。
2. 正整数 $n$ に対する $D^n$ を求めよ。
3. $A^n$ を求めよ。
', '$$P^{-1}=\begin{pmatrix}1&-1\\0&1\end{pmatrix},\quad A=\begin{pmatrix}2&2\\0&4\end{pmatrix}.$$
$$D^n=\begin{pmatrix}2^n&0\\0&4^n\end{pmatrix},\quad A^n=\begin{pmatrix}2^n&4^n-2^n\\0&4^n\end{pmatrix}.$$
', '$A=PDP^{-1}$ なので積の途中の $P^{-1}P$ が打ち消され、$A^n=PD^nP^{-1}$。
対角行列の累乗は対角成分をそれぞれ累乗すればよい。最後に $P$ と $P^{-1}$ を掛ける。
使用する知識：[対角化](/knowledge/55555555-5555-4555-8555-555555555554)、[行列の累乗](/knowledge/55555555-5555-4555-8555-555555555555)。
', NULL) ON CONFLICT DO NOTHING;

-- problem_genres
INSERT INTO public.problem_genres (problem_id, genre_id) VALUES ('66666666-6666-4666-8666-666666666661', '33333333-3333-4333-8333-333333333333') ON CONFLICT DO NOTHING;
INSERT INTO public.problem_genres (problem_id, genre_id) VALUES ('66666666-6666-4666-8666-666666666662', '33333333-3333-4333-8333-333333333333') ON CONFLICT DO NOTHING;
INSERT INTO public.problem_genres (problem_id, genre_id) VALUES ('66666666-6666-4666-8666-666666666663', '33333333-3333-4333-8333-333333333333') ON CONFLICT DO NOTHING;

-- problem_knowledge
INSERT INTO public.problem_knowledge (problem_id, knowledge_id) VALUES ('66666666-6666-4666-8666-666666666661', '55555555-5555-4555-8555-555555555551') ON CONFLICT DO NOTHING;
INSERT INTO public.problem_knowledge (problem_id, knowledge_id) VALUES ('66666666-6666-4666-8666-666666666661', '55555555-5555-4555-8555-555555555552') ON CONFLICT DO NOTHING;
INSERT INTO public.problem_knowledge (problem_id, knowledge_id) VALUES ('66666666-6666-4666-8666-666666666661', '55555555-5555-4555-8555-555555555553') ON CONFLICT DO NOTHING;
INSERT INTO public.problem_knowledge (problem_id, knowledge_id) VALUES ('66666666-6666-4666-8666-666666666662', '55555555-5555-4555-8555-555555555551') ON CONFLICT DO NOTHING;
INSERT INTO public.problem_knowledge (problem_id, knowledge_id) VALUES ('66666666-6666-4666-8666-666666666662', '55555555-5555-4555-8555-555555555552') ON CONFLICT DO NOTHING;
INSERT INTO public.problem_knowledge (problem_id, knowledge_id) VALUES ('66666666-6666-4666-8666-666666666662', '55555555-5555-4555-8555-555555555554') ON CONFLICT DO NOTHING;
INSERT INTO public.problem_knowledge (problem_id, knowledge_id) VALUES ('66666666-6666-4666-8666-666666666663', '55555555-5555-4555-8555-555555555554') ON CONFLICT DO NOTHING;
INSERT INTO public.problem_knowledge (problem_id, knowledge_id) VALUES ('66666666-6666-4666-8666-666666666663', '55555555-5555-4555-8555-555555555555') ON CONFLICT DO NOTHING;

COMMIT;
