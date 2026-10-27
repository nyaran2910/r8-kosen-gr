import { Suspense } from "react";
import AttemptHome from "@/components/attempt-home";

export default function AttemptPage() {
  return (
    <Suspense fallback={<p>演習を読み込んでいます。</p>}>
      <AttemptHome />
    </Suspense>
  );
}
