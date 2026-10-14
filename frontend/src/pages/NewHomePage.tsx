import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

/** Temporary restore marker - full file follows in next commit if truncated */
export default function NewHomePage() {
  return (
    <div dir="rtl" style={{ padding: 24 }}>
      <h1>HBI</h1>
      <p>در حال بازیابی فایل هوم‌پیج… لطفاً یک لحظه صبر کنید یا صفحه را تازه کنید.</p>
      <p><a href="/">تلاش مجدد</a></p>
    </div>
  );
}
