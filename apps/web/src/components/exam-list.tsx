"use client";

import useSWR from "swr";
import Link from "next/link";

type ExamSummary = {
  id: string;
  name: string;
  category: string;
  subject_id: string;
  subject_name: string;
};

async function fetchExams(url: string): Promise<ExamSummary[] | null> {
  const response = await fetch(url, { cache: "no-store" });

  if (response.status === 401) {
    return null;
  }

  if (!response.ok) {
    throw new Error("試験一覧を取得できませんでした。");
  }

  return response.json();
}

export default function ExamList() {
  const { data, error, isLoading, mutate } = useSWR("/api/exams", fetchExams, {
    shouldRetryOnError: false,
  });

  if (error) {
    return (
      <div>
        <p>試験一覧を取得できませんでした。</p>
        <button type="button" onClick={() => mutate()}>
          再試行
        </button>
      </div>
    );
  }

  if (isLoading) return <p>試験一覧を読み込んでいます。</p>;
  if (!data) return <p>ログインし直してください。</p>;
  if (data.length === 0) return <p>試験はまだ登録されていません。</p>;

  return (
    <section>
      <h2>対象試験</h2>
      <ul>
        {data.map((exam) => (
          <li key={exam.id}>
            <Link href={`/exams/${exam.id}`}>{exam.name}</Link>: {exam.category}/{exam.subject_name}
          </li>
        ))}
      </ul>
    </section>
  );
}
