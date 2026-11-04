import { describe, expect, it } from 'vitest'
import { splitMarks } from './marks'

describe('splitMarks', () => {
  it('splits matched words from the rest', () => {
    expect(splitMarks('the \u0002saw\u0003 and \u0002table\u0003')).toEqual([
      { text: 'the ', marked: false },
      { text: 'saw', marked: true },
      { text: ' and ', marked: false },
      { text: 'table', marked: true },
    ])
  })

  it('leaves text without marks alone', () => {
    expect(splitMarks('plain')).toEqual([{ text: 'plain', marked: false }])
    expect(splitMarks('')).toEqual([])
  })

  it('keeps markup as text', () => {
    expect(splitMarks('<b>\u0002x\u0003</b>')).toEqual([
      { text: '<b>', marked: false },
      { text: 'x', marked: true },
      { text: '</b>', marked: false },
    ])
  })

  it('copes with an unclosed mark', () => {
    expect(splitMarks('a \u0002b')).toEqual([
      { text: 'a ', marked: false },
      { text: 'b', marked: true },
    ])
  })
})
