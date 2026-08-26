import { apiClient } from '@/api/client'

function savePdf(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(url)
}

function reportFilename(filename?: string) {
  return (filename?.replace(/[<>:"/\\|?*]/g, '-').trim() || 'venturemind-evaluation-report') + '.pdf'
}

export const reportApi = {
  generate: async (projectId: string, evaluationId: string, filename?: string) => {
    const response = await apiClient.post(`/projects/${projectId}/evaluations/${evaluationId}/report`, undefined, { responseType: 'blob' })
    savePdf(response.data, reportFilename(filename ?? `venturemind-${evaluationId}`))
  },
  download: async (projectId: string, evaluationId: string, reportId: string, filename?: string) => {
    const response = await apiClient.get(`/projects/${projectId}/evaluations/${evaluationId}/report/downloads/${reportId}`, { responseType: 'blob' })
    savePdf(response.data, reportFilename(filename ?? `venturemind-${evaluationId}`))
  },
}
