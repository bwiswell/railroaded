export default function unique<T> (data: T[]): T[] {
    return [...new Set(data)]
}