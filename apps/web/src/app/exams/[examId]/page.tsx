import { Suspense } from "react";
import ExamHome from "@/components/exam-home";

export default function ExamPage() {
  return (
    <Suspense fallback={<p>試験を読み込んでいます。</p>}>
      <ExamHome />
    </Suspense>
  );
}
