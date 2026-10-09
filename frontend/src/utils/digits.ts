/** تبدیل ارقام فارسی/عربی به لاتین — بک‌اند فقط عدد لاتین قبول می‌کند */
export function fa2en(input: string): string {
  return input
    .replace(/[۰-۹]/g, (d) => String('۰۱۲۳۴۵۶۷۸۹'.indexOf(d)))
    .replace(/[٠-٩]/g, (d) => String('٠١٢٣٤٥٦٧٨٩'.indexOf(d)));
}
