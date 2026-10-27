export async function fetchJson(url: string) {
  const response = await fetch(url, { cache: "no-store" });

  if (response.status === 401) {
    throw new Error("ログインしてください。");
  }

  if (response.status === 404) {
    throw new Error("対象が見つかりません。");
  }

  if (!response.ok) {
    throw new Error("取得に失敗しました。");
  }

  return response.json();
}
