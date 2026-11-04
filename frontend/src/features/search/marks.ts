const MARK_START = '\u0002'
const MARK_END = '\u0003'

export type Part = { text: string; marked: boolean }

/** Splits search API text into plain and matched parts. Rendered as text, never HTML. */
export function splitMarks(text: string): Part[] {
  const [before, ...rest] = text.split(MARK_START)
  const parts: Part[] = [{ text: before, marked: false }]
  for (const chunk of rest) {
    const end = chunk.indexOf(MARK_END)
    if (end === -1) {
      parts.push({ text: chunk, marked: true })
    } else {
      parts.push({ text: chunk.slice(0, end), marked: true })
      parts.push({ text: chunk.slice(end + 1), marked: false })
    }
  }
  return parts.filter((part) => part.text !== '')
}
