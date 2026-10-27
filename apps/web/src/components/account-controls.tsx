"use client";

import ExamList from "@/components/exam-list";
import useSWR from "swr";

type CurrentUser = {
  id: string;
};

async function fetchCurrentUser(url: string): Promise<CurrentUser | null> {
  const response = await fetch(url, { cache: "no-store" });

  if (response.status === 401) {
    return null;
  }

  if (!response.ok) {
    throw new Error("ログイン状態を取得できませんでした。");
  }

  return response.json();
}

export default function AccountControls() {
  const { data, error, isLoading, mutate } = useSWR(
    "/api/auth/me",
    fetchCurrentUser,
    { shouldRetryOnError: false },
  );

  if (error) {
    return (
      <div>
        <p>ログイン状態を取得できませんでした。</p>
        <button type="button" onClick={() => mutate()}>
          再試行
        </button>
      </div>
    );
  }

  if (isLoading) {
    return <p>ログイン状態を確認しています。</p>;
  }

  if (!data) {
    return <a href="/api/auth/google/login">Googleでログイン</a>;
  }

  return (
    <div>
      <p>ログインしています。</p>
      <form action="/api/auth/logout" method="post">
        <button type="submit">ログアウト</button>
      </form>
      <ExamList />
    </div>
  );
}
