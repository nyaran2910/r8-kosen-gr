"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import Markdown from "react-markdown"; // MDを表示してくれるコンポーネント
import remarkGfm from "remark-gfm"; // 表・取り消し線などの文法を認識する
import remarkMath from "remark-math"; // 数式の構文を認識する
import rehypeKatex from "rehype-katex"; // 数式を描画する
import useSWR from "swr";
import { fetchJson } from "@/lib/api";

import StartAttempt from "@/components/start-attempt"

type ExamDetail = {
  id: string;
  name: string;
  category: string;
  subject_name: string;
  problems: { id: string; body_md: string }[];
};

export default function ExamHome() {
  const { examId } = useParams<{ examId: string }>();
  const { data, error, isLoading, mutate } = useSWR<ExamDetail>(
    `/api/exams/${examId}`,
    fetchJson,
    { shouldRetryOnError: false },
  );

  if (error) {
    return (
      <div>
        <p>{error.message}</p>
        <a href="/api/auth/google/login">Googleでログイン</a>
        <button type="button" onClick={() => mutate()}>
          再試行
        </button>
      </div>
    );
  }

  if (isLoading || !data) return <p>試験を読み込んでいます。</p>;

  return (
    <main>
      <Link href="/">試験選択へ戻る</Link>

      <h1>{data.name}</h1>
      <p>
        {data.category}／{data.subject_name}
      </p>

      <StartAttempt key={data.id} examId={data.id} />

      <h2>問題のプレビュー</h2>

      <p>この表示では演習の記録・時間計測は始まりません。</p>

      {data.problems.length === 0 && <p>問題はまだ登録されていません。</p>}
      {data.problems.map((problem, index) => (
        <details key={problem.id}>
          {" "}
          {/*　detailとsummaryでかいへするやつ。summaryは閉じてても見える。*/}
          <summary>問題{index + 1}の本文を確認</summary>
          <Markdown
            remarkPlugins={[remarkGfm, remarkMath]}
            rehypePlugins={[[rehypeKatex, { trust: false }]]} // trust:falseで数式ないのリンクといった危ない処理を無効化する。
            skipHtml // MDないのHTML構文を無視する
          >
            {problem.body_md}
            {/* こうやって渡すとコンポーネント内では(childre)つって参照する */}
          </Markdown>
        </details>
      ))}
    </main>
  );
}
