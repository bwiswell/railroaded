type SplitFilter<T> = (element: T) => boolean


type SplitOutput<T> = {
    truthy: T[],
    falsy: T[]
}


export default function split<T> (
            elements: T[], 
            filter: SplitFilter<T>
        ): SplitOutput<T> {
    const truthy: T[] = []
    const falsy: T[] = []
    elements.forEach((element: T) => 
        filter(element) ? truthy.push(element) : falsy.push(element)
    )
    return { truthy, falsy }
}