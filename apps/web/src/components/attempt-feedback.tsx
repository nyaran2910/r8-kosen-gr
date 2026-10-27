"use client";

import { useState } from "react";
import useSWR from "swr";

const results = {
  perfect: "完璧",
  correct: "正解",
  incorrect: "不正解",
  gave_up: "あきらめた",
};

type Result = keyof typeof results;

type Draft = {
  result: Result | null;
  knowledge: Record<string, boolean>;
};

type Props = {
  attemptId: string;
  knowledgeElements: { id: string; title: string }[];
};

// 保存済み下書きを読む。SWRのfetcherなので、ブラウザー側で実行される。
// 型宣言だけでは保存データを検証できないため、値も確認する。
// 小さな固定形式なので、追加ライブラリを入れずここで検証する。
async function readDraft(key: string): Promise<Draft> {
  const empty: Draft = { result: null, knowledge: {} };
  const raw = sessionStorage.getItem(key);
  if (!raw) return empty;

  try {
    const saved = JSON.parse(raw);
    if (!saved || typeof saved !== "object") return empty;

    const result: Result | null =
      typeof saved.result === "string" &&
      Object.hasOwn(results, saved.result)
        ? saved.result as Result
        : null;

    // true/falseだけ復元し、壊れた値や古い形式を採用しない。
    const knowledge: Record<string, boolean> = {};
    if (saved.knowledge && typeof saved.knowledge === "object") {
      for (const [id, value] of Object.entries(saved.knowledge)) {
        if (typeof value === "boolean") knowledge[id] = value;
      }
    }

    return { result, knowledge };
  } catch {
    // 壊れたJSONは未入力として扱い、次の入力で保存し直す。
    return empty;
  }
}

export default function AttemptFeedback({
  attemptId,
  knowledgeElements,
}: Props) {
  // 演習ごとに保存先を分ける。v1は下書きの形式の版。
  // この接頭辞を使い、ログアウト時に下書きだけを消す。
  const storageKey = `learning:feedback:v1:${attemptId}`;

  // 読み込み状態と画面内の下書き管理は、既存のSWRへ任せる。
  // フォーカス復帰などで、入力中の状態を読み直さない設定にする。
  const { data: draft, error, mutate } = useSWR<Draft>(
    storageKey,
    readDraft,
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: false,
      revalidateIfStale: false,
      shouldRetryOnError: false,
    },
  );

  // 保存領域が使えない場合、画面内の入力は保持して注意を表示する。
  const [storageError, setStorageError] = useState("");

  // 入力変更時に保存し、SWRの表示も更新する。
  // 自動保存Effectを使わず、復元前の空データによる上書きを防ぐ。
  function updateDraft(next: Draft) {
    try {
      sessionStorage.setItem(storageKey, JSON.stringify(next));
      setStorageError("");
    } catch {
      setStorageError(
        "下書きを保存できません。再読み込みすると入力が失われます。",
      );
    }
    void mutate(next, { revalidate: false });
  }

  if (error) {
    return (
      <section>
        <p role="alert">下書きを読み込めませんでした。</p>
        <button type="button" onClick={() => mutate()}>再試行</button>
      </section>
    );
  }
  if (!draft) return <p>評価の下書きを読み込んでいます。</p>;

  // falseは「わからない」という入力済みの値。
  // truthy判定ではなく、booleanかどうかで選択済みを確認する。
  const complete =
    draft.result !== null &&
    knowledgeElements.every(
      (item) => typeof draft.knowledge[item.id] === "boolean",
    );

  return (
    <section>
      <h2>演習の評価</h2>
      <fieldset>
        <legend>問題全体の結果</legend>
        {(Object.entries(results) as [Result, string][]).map(
          ([value, label]) => (
            <label key={value}>
              <input
                type="radio"
                name={`result-${attemptId}`}
                checked={draft.result === value}
                onChange={() => updateDraft({ ...draft, result: value })}
              />
              {label}
            </label>
          ),
        )}
      </fieldset>

      {knowledgeElements.map((item) => (
        <fieldset key={item.id}>
          <legend>{item.title}</legend>
          {[true, false].map((understood) => (
            <label key={String(understood)}>
              <input
                type="radio"
                name={`knowledge-${attemptId}-${item.id}`}
                checked={draft.knowledge[item.id] === understood}
                onChange={() => updateDraft({
                  ...draft,
                  knowledge: {
                    ...draft.knowledge,
                    [item.id]: understood,
                  },
                })}
              />
              {understood ? "わかった" : "わからない"}
            </label>
          ))}
        </fieldset>
      ))}

      {storageError && <p role="alert">{storageError}</p>}
      <p>
        {complete ? "全項目を選択済みです。" : "全項目を選択してください。"}
        現在は下書きのみで、評価はまだ確定されません。
      </p>
    </section>
  );
}
