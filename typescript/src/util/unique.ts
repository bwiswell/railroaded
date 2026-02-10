export default function unique<T> (data: T[]): T[] {
    return data.filter((val, idx, arr) => arr.indexOf(val) === idx)
}