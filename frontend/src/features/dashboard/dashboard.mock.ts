export const dashboardData = {
  userName: 'Founder',
  summary: [
    { label: 'Active ideas', value: '3', change: '+1 this month' },
    { label: 'Average confidence', value: '76%', change: '+4% from last month' },
    { label: 'Reports generated', value: '5', change: '2 ready to download' },
  ],
  latestIdea: { name: 'CareLink', industry: 'Digital health', score: 78, status: 'Evaluation complete' },
  scoreBreakdown: [
    { metric: 'Innovation', score: 82 }, { metric: 'Market', score: 84 }, { metric: 'Business model', score: 72 },
    { metric: 'Scalability', score: 77 }, { metric: 'Technical', score: 74 }, { metric: 'Financial', score: 69 },
  ],
  trend: [
    { month: 'Feb', score: 61 }, { month: 'Mar', score: 65 }, { month: 'Apr', score: 68 }, { month: 'May', score: 71 }, { month: 'Jun', score: 74 }, { month: 'Jul', score: 78 },
  ],
  ideas: [
    { name: 'CareLink', industry: 'Digital health', stage: 'MVP', score: 78, updated: 'Today' },
    { name: 'LoopCart', industry: 'Circular commerce', stage: 'Research', score: 74, updated: '3 days ago' },
    { name: 'SkillBridge', industry: 'EdTech', stage: 'Idea', score: 67, updated: 'Last week' },
  ],
  risks: [
    { label: 'Market risk', level: 'Moderate', tone: 'bg-amber-500', detail: 'Validate willingness to pay.' },
    { label: 'Financial risk', level: 'High', tone: 'bg-red-500', detail: 'Refine unit economics assumptions.' },
    { label: 'Technical risk', level: 'Low', tone: 'bg-emerald-500', detail: 'MVP scope is achievable.' },
  ],
  reports: [
    { name: 'CareLink evaluation report', date: '12 Jul 2026', status: 'Ready' },
    { name: 'LoopCart market assessment', date: '09 Jul 2026', status: 'Ready' },
    { name: 'SkillBridge opportunity brief', date: '05 Jul 2026', status: 'Ready' },
  ],
}
