export function joinStyles(styles: (string | false | undefined)[]) {
  return styles.filter(Boolean).join(' ');
}