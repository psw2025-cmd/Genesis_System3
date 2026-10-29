export type ChecklistItem = {
  id?: string
  label?: string
  pass?: boolean
  detail?: string
}

export function showField(value: unknown): string {
  if (value === null || value === undefined || value === '') return 'null'
  if (typeof value === 'boolean') return value ? 'true' : 'false'
  return String(value)
}

export function ValidationChecklist({ items }: { items: ChecklistItem[] | null | undefined }) {
  if (items == null) {
    return <div data-testid="validations-checklist">validations_checklist: null</div>
  }
  if (items.length === 0) {
    return <div data-testid="validations-checklist">validations_checklist: empty</div>
  }
  return (
    <div data-testid="validations-checklist">
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
        <thead>
          <tr>
            <th className="thead">Check</th>
            <th className="thead">Result</th>
            <th className="thead">Detail</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item, index) => {
            const passed = item.pass === true
            const detail = showField(item.detail)
            const stub = /stub/i.test(detail)
            const paperMissing = item.pass === false && (
              item.id === 'paper_validations_exists' || /paper_validations/i.test(`${item.id || ''} ${item.label || ''} ${detail}`)
            ) && /missing|\bNO\b/i.test(detail)
            return (
              <tr key={item.id || `${item.label || 'check'}-${index}`}>
                <td className="tcell">{item.label || item.id || 'null'}</td>
                <td className="tcell" style={{ color: passed ? 'var(--up)' : 'var(--down)', fontWeight: 800 }}>
                  {item.pass === true ? 'YES' : item.pass === false ? 'NO' : showField(item.pass)}
                  {stub ? ' · STUB' : ''}
                  {paperMissing ? ' · MISSING' : ''}
                </td>
                <td className="tcell">{detail}</td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
