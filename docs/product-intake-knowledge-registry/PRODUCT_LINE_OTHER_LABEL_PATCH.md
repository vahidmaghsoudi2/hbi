# Product Line label: OTHER → عطر و ادکلن

## Change (2 lines in `frontend/src/pages/ProductIntakePanel.tsx`)

```diff
-  { value: "OTHER", label: "متفرقه (OTHER)" },
+  { value: "OTHER", label: "عطر و ادکلن (OTHER)" },

-      setErr("انتخاب لاین محصول (پوست / مو / زیبایی / ابزار / متفرقه) الزامی است.");
+      setErr("انتخاب لاین محصول (پوست / مو / زیبایی / ابزار / عطر و ادکلن) الزامی است.");
```

## Constraints
- Code value remains `OTHER` (no schema / allowlist / migration change)
- BEAUTY = آرایشی; HAIR includes رنگ مو (owner decision)
- No ProductKnowledge / Gate 0 impact
