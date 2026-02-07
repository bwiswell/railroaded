import csv from 'csv-parser'
import fs from 'fs'


export function isSameDay (dateA: Date, dateB: Date): boolean {
    return (
        dateA.getFullYear() === dateB.getFullYear() &&
        dateA.getMonth() === dateB.getMonth() &&
        dateA.getDate() === dateB.getDate()
    );
}


export function includesDay (day: Date, dates: Date[]): boolean {
    return dates.some(date => isSameDay(day, date))
}


type ParseOptions<T> = {
    interpolateCols?: { [key: string]: (record: Partial<T>) => any },
    intCols?: string[],
    floatCols?: string[],
    renameCols?: { [key: string]: string },
    transformEnums?: { [key: string]: (value: number) => any }
}

export async function loadList<T extends {}> (
            path: string,
            options: ParseOptions<T> = {}
        ): Promise<T[]> {
    return new Promise((resolve, reject) => {
        const results: Partial<T>[] = [];
        fs.createReadStream(path)
            .pipe(csv({
                mapHeaders: ({ header }) => {
                    if (options.renameCols && options.renameCols[header]) {
                        return options.renameCols[header]
                    } else {
                        return header
                    }
                },
                mapValues: ({ header, index, value }) => {
                    if (options.intCols && options.intCols.includes(header)) {
                        return parseInt(value, 10);
                    } else if (
                                options.floatCols && 
                                options.floatCols.includes(header)
                            ) {
                        return parseFloat(value);
                    } else if (
                                options.transformEnums && 
                                options.transformEnums[header]
                            ) {
                        return options.transformEnums[header](
                            parseInt(value, 10)
                        )
                    }
                }
            }))
            .on('data', (data: Partial<T>) => {
                if (options.interpolateCols) {
                    Object.keys(options.interpolateCols).forEach(
                        col => {
                            const func = options.interpolateCols![col]!
                            data[col as keyof T] = func(data)
                        }
                    )
                }
                results.push(data)
            })
            .on('end', () => resolve(results as T[]))
            .on('error', (error: string) => reject(error))
    });
}

type SplitFilter<T> = (element: T) => boolean

type SplitOutput<T> = {
    truthy: T[],
    falsy: T[]
}

export function split<T> (
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