export default function filterObject<T> (
            obj: Record<string, T>,
            filter: (value: T) => boolean
        ): Record<string, T> {
    return Object.keys(obj).reduce(
        (prev, curr) => {
            if (filter(obj[curr]!)) prev[curr] = obj[curr] as T
            return prev
        },
        {} as Record<string, T>
    )
}