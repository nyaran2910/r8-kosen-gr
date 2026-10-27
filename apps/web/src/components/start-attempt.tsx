"use client";

import Link from "next/link";
import { useRef, useState } from "react";

type Reservation = {
  id: string;
  resumed: boolean;
};

export default function StartAttempt({ examId }: { examId: string }) {
  const operationId = useRef<string | null>(null);

  const [pending, setPending] = useState(false);
  const [error, setError] = useState("");
  const [reservation, setReservation] = useState<Reservation | null>(null);

  async function reserveAttempt() {
    setPending(true);
    setError("");

    try {
      // 通信に失敗して再試行するときも、同じIDを送る。
      operationId.current ??= crypto.randomUUID();

      const response = await fetch("/api/attempts/next", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          id: operationId.current,
          exam_id: examId,
        }),
      });

      if (response.status === 401) {
        throw new Error("ログインしてください。");
      }

      const result = await response.json();

      // 既に演習があれば、その演習へのリンクを表示する。
      if (
        response.status === 409 &&
        typeof result.detail?.active_attempt_id === "string"
      ) {
        setReservation({
          id: result.detail.active_attempt_id,
          resumed: true,
        });
        return;
      }

      if (!response.ok) {
        throw new Error("演習を準備できませんでした。再試行してください。");
      }

      if (result.id === null) {
        setError("この試験には利用できる問題がありません。");
        return;
      }

      setReservation({ id: result.id, resumed: false });
    } catch (error) {
      setError(
        error instanceof Error ? error.message : "通信に失敗しました。",
      );
    } finally {
      setPending(false);
    }
  }

  if (reservation) {
    return (
      <section> {/* <div>とほぼ同じ */}
        <p>
          {reservation.resumed
            ? "途中の演習があります。別の試験の演習の場合もあります。"
            : "演習を準備しました。問題画面を開くと時間計測を開始します。"}
        </p>
        <Link href={`/attempts/${encodeURIComponent(reservation.id)}`}>
          {reservation.resumed ? "途中の演習を再開する" : "問題画面へ進む"}
        </Link>
      </section>
    );
  }

  return (
    <section>
      <button
        type="button"
        onClick={reserveAttempt}
        disabled={pending}
      >
        {pending ? "演習を準備しています…" : "演習を始める"}
      </button>
      {error && <p role="alert">{error}</p>}
    </section>
  );
}
