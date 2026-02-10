import {
    BlobReader,
    TextWriter,
    ZipReader
} from '@zip.js/zip.js'


export default async function unzip (
            blob: Blob,
            subdirectory?: string
        ): Promise<Record<string, string>> {
    const entries = await new ZipReader(new BlobReader(blob)).getEntries()
        .then(entries => entries.filter(e => !e.directory))
        .then(
            entries => subdirectory ? 
                entries.filter(
                    entry => entry.filename.split('/')[0] === subdirectory
                ) : entries
        )

    const writer = new TextWriter()
    const names = entries
        .map(entry => entry.filename.split('/'))
        .map(parts => parts[parts.length - 1]!)
    const text = await Promise.all(
        entries.map(entry => entry.getData<string>(writer))
    )
    return names.reduce(
        (prev, curr, idx) => {
            prev[curr] = text[idx]!
            return prev
        },
        {} as Record<string, string>
    )
}
