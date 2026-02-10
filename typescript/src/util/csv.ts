import csv from 'csv-parser'
import { Readable } from 'stream';


export async function loadList<T extends {}> (contents: string): Promise<T[]> {
    return new Promise((resolve, reject) => {
        const results: Partial<T>[] = [];
        Readable.from(contents)
            .pipe(csv())
            .on('data', (data: Partial<T>) => results.push(data))
            .on('end', () => resolve(results as T[]))
            .on('error', (error: string) => reject(error))
    });
}

