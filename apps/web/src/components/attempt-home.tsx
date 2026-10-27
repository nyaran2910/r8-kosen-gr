"use client"; // ブラウザー側でHooksやイベント処理を使う。

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import useSWR from "swr";
import { fetchJson } from "@/lib/api";

import AttemptAnswer from "@/components/attempt-answer";

// APIが返す演習データの型。
// 日時はJSONでは文字列になり、未記録ならnullになる。
type AttemptDetail = {
  id: string;
  exam_id: string;
  problem_id: string;
  body_md: string;
  started_at: string | null;
  answer_viewed_at: string | null;
  submitted_at: string | null;
  closed_at: string | null;
  answer_md: string | null;
  explanation_md: string | null;
  knowledge_elements: {
    id: string;
    title: string;
  }[];
};

export default function AttemptHome() {
  // /attempts/[attemptId]の[attemptId]部分を取り出す。
  const { attemptId } = useParams<{ attemptId: string }>();

  // attemptIdは子へ渡すデータ。
  // keyが変わると子が作り直され、エラーなどの状態も初期化される。
  return <AttemptBody key={attemptId} attemptId={attemptId} />;
}

function AttemptBody({ attemptId }: { attemptId: string }) {
  // 演習データの取得・キャッシュ・読み込み状態の管理をSWRに任せる。
  // mutateは取得済みデータの更新や再取得に使う。
  const { data, error, isLoading, mutate } = useSWR<AttemptDetail>(
    `/api/attempts/${attemptId}`,
    fetchJson,
    { shouldRetryOnError: false }, // 失敗時の自動再試行を止める。
  );

  // 開始通知のエラーメッセージを保持する。
  const [startError, setStartError] = useState("");

  // この値を増やすことで、開始通知のEffectを再実行する。
  const [retryCount, setRetryCount] = useState(0);

  // データがあり、未開始・未確定・未終了なら開始通知が必要。
  // Booleanで式の結果を必ずtrueかfalseにする。
  const needsStart = Boolean(
    data && !data.started_at && !data.submitted_at && !data.closed_at,
  );

  // 画面への反映後、必要ならAPIに開始通知を送る。
  useEffect(() => {
    if (!needsStart) return;

    // 画面を離れた後に、古い通信結果を反映しないためのフラグ。
    let cancelled = false;

    async function notifyStart() {
      try {
        // 開始時刻の記録はデータを変更するのでPOSTを使う。
        const response = await fetch(`/api/attempts/${attemptId}/start`, {
          method: "POST",
          cache: "no-store",
        });

        if (response.status === 401) {
          throw new Error("ログインしてください。");
        }
        if (!response.ok) {
          throw new Error("開始時刻を記録できませんでした。");
        }

        // 開始時刻が入った演習データを受け取る。
        const started: AttemptDetail = await response.json();

        if (!cancelled) {
          // SWRのデータを更新し、開始時刻を画面に表示する。
          // 必要なデータは返っているので、直後の再取得は省く。
          await mutate(started, { revalidate: false });
        }
      } catch (error) {
        if (!cancelled) {
          // catchした値はErrorとは限らないので型を確認する。
          setStartError(
            error instanceof Error ? error.message : "通信に失敗しました。",
          );
        }
      }
    }

    // 非同期処理を開始する。Effect自体はasync関数にしない。
    void notifyStart();

    // 画面を離れるときや、Effectの再実行前に呼ばれる。
    // 通信やAPIの処理そのものを取り消すわけではない。
    return () => {
      cancelled = true;
    };
  }, [attemptId, needsStart, retryCount, mutate]);
  // 上の依存値が変わるとEffectを再実行する。
  // 開始記録が成功するとneedsStartがfalseになり、通知を止める。

  // 演習データの取得に失敗した場合の表示。
  if (error) {
    return (
      <div>
        <p role="alert">{error.message}</p>
        <a href="/api/auth/google/login">Googleでログイン</a>
        <button type="button" onClick={() => mutate()}>
          再試行
        </button>
      </div>
    );
  }

  // データがまだなければ、本文を表示せず待つ。
  if (isLoading || !data) return <p>演習を読み込んでいます。</p>;

  return (
    <main>
      <Link href={`/exams/${data.exam_id}`}>試験画面へ戻る</Link>
      <h1>演習</h1>

      {/* 確定・終了・開始済み・開始通知中の順で状態を表示する。 */}
      {data.submitted_at ? (
        <p>確定済みの演習です。</p>
      ) : data.closed_at ? (
        <p>終了した演習です。</p>
      ) : data.started_at ? (
        <p>
          開始時刻：
          {new Date(data.started_at).toLocaleString("ja-JP")}
        </p>
      ) : (
        <p>開始時刻を記録しています…</p>
      )}

      {/* 開始通知が必要で、通知に失敗した場合だけ表示する。 */}
      {needsStart && startError && (
        <div>
          <p role="alert">{startError}</p>
          <button
            type="button"
            onClick={() => {
              setStartError(""); // 前回のエラー表示を消す。
              setRetryCount((count) => count + 1); // Effectを再実行する。
            }}
          >
            開始通知を再試行
          </button>
        </div>
      )}

      {/* Markdown本文を表示する。表・数式にも対応する。 */}
      <Markdown
        remarkPlugins={[remarkGfm, remarkMath]}
        rehypePlugins={[[rehypeKatex, { trust: false }]]}
        skipHtml
      >
        {data.body_md}
      </Markdown>

      {/* 開始通知が成功してから解答閲覧を許可する。 */}
      <AttemptAnswer
        attemptId={data.id}
        canReveal={Boolean(
          data.started_at && !data.submitted_at && !data.closed_at,
        )}
        answerMd={data.answer_md}
        explanationMd={data.explanation_md}
        onRevealed={async () => {
          await mutate();
        }}
      />

      {/* 閲覧時刻はAPIの記録を使い、解答取得前には表示しない。 */}
      {data.answer_viewed_at && (
        <section>
          <h2>評価対象の知識</h2>

          {data.knowledge_elements.length === 0 ? (
            // 紐付けがない問題でも、空の状態を明示する。
            <p>この問題には知識要素が紐付けられていません。</p>
          ) : (
            <ul>
              {data.knowledge_elements.map((knowledge) => (
                // 同じ名称があっても区別できるよう、IDをkeyに使う。
                <li key={knowledge.id}>{knowledge.title}</li>
              ))}
            </ul>
          )}
        </section>
      )}
    </main>
  );
}
