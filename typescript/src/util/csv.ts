import csv from 'csv-parser'
import fs from 'fs'


export async function loadList<T extends {}> (path: string): Promise<T[]> {
    return new Promise((resolve, reject) => {
        const results: Partial<T>[] = [];
        fs.createReadStream(path)
            .pipe(csv())
            .on('data', (data: Partial<T>) => results.push(data))
            .on('end', () => resolve(results as T[]))
            .on('error', (error: string) => reject(error))
    });
}

