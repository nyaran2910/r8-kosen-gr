"use client";

// Markdownの解析・数式描画は、問題本文と同じライブラリに任せる。
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";

// ボタン操作で行うPOSTの状態管理に使う。
// 通常のuseSWRと違い、画面を開いただけでは通信を開始しない。
import useSWRMutation from "swr/mutation";

// 解答閲覧POSTが返すデータ。
// 成功時には閲覧時刻・解答・解説が必ず入る。
type AnswerResult = {
  id: string;
  answer_viewed_at: string;
  answer_md: string;
  explanation_md: string;
};

// 親の演習画面から受け取る情報。
type AnswerProps = {
  attemptId: string; // 操作対象の演習ID。
  canReveal: boolean; // 開始済み・未確定・未終了ならtrue。
  answerMd: string | null; // GETで取得した閲覧済み解答。未閲覧ならnull。
  explanationMd: string | null; // GETで取得した解説。
  // 解答閲覧に成功したことを親へ通知する。
  // 親は演習情報を再取得し、閲覧時刻と評価対象を更新する。
  onRevealed: () => Promise<void>;
};

// SWRが呼び出す通信処理。
// 引数は解答閲覧APIのURL、戻り値は表示に使う解答データ。
async function revealAnswer(url: string): Promise<AnswerResult> {
  // 閲覧時刻を記録するためPOSTを使う。
  // 対象IDはURLに含まれるので、リクエスト本文は不要。
  const response = await fetch(url, {
    method: "POST",
    cache: "no-store",
  });

  if (response.status === 401) {
    throw new Error("ログインしてください。");
  }
  if (response.status === 409) {
    throw new Error("現在の演習状態では解答を開けません。");
  }
  if (!response.ok) {
    throw new Error("解答を取得できませんでした。再試行してください。");
  }

  // 日時はJSONの文字列として受け取る。
  return response.json();
}

// 解答閲覧ボタンと、取得済みの解答・解説を表示する。
export default function AttemptAnswer({
  attemptId,
  canReveal,
  answerMd,
  explanationMd,
  onRevealed,
}: AnswerProps) {
  // triggerは通信開始、isMutatingは処理中、errorは失敗情報。
  // dataには成功したPOSTの結果が入り、画面表示に使える。
  const { trigger, data, error, isMutating } = useSWRMutation(
    `/api/attempts/${attemptId}/answer`,
    revealAnswer,
  );

  // POST直後はその結果を表示し、再読み込み後は親のGET結果を使う。
  // 解答本文をsessionStorageなどへ別途保存する必要はない。
  const answer = data?.answer_md ?? answerMd;
  const explanation = data?.explanation_md ?? explanationMd;

  return (
    <section>
      {/* 未閲覧のときだけボタンを表示する。 */}
      {answer === null && (
        <button
          type="button"
          disabled={!canReveal || isMutating}
          onClick={async () => {
            try {
              // 成功するとSWRのdataが更新され、解答が表示される。
              await trigger();
            } catch {
              // エラーはSWRのerrorに入るため、下の表示へ任せる。
              // イベント処理から未処理のPromise例外を出さない。
            }
          }}
        >
          {isMutating ? "解答を取得しています…" : "解答を見る"}
        </button>
      )}

      {error && <p role="alert">{error.message}</p>}

      {/* 空文字列と未取得のnullを区別するため、nullと比較する。 */}
      {answer !== null && (
        <>
          <h2>解答</h2>
          <Markdown
            remarkPlugins={[remarkGfm, remarkMath]}
            rehypePlugins={[[rehypeKatex, { trust: false }]]}
            skipHtml
          >
            {answer}
          </Markdown>

          <h2>解説</h2>
          <Markdown
            remarkPlugins={[remarkGfm, remarkMath]}
            rehypePlugins={[[rehypeKatex, { trust: false }]]}
            skipHtml
          >
            {explanation ?? ""}
          </Markdown>
        </>
      )}
    </section>
  );
}
