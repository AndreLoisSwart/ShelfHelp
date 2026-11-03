/** A UTC timestamp from the API, as a local date. */
export const formatDate = (iso: string) =>
  new Date(iso).toLocaleDateString(undefined, { day: 'numeric', month: 'short', year: 'numeric' })

export const plural = (count: number, noun: string) => `${count} ${noun}${count === 1 ? '' : 's'}`
