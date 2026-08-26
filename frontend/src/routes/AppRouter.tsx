import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { AppShell } from '@/components/layout/AppShell'
import { NotFoundPage } from '@/pages/NotFoundPage'
import { LoginPage } from '@/features/auth/LoginPage'
import { RegisterPage } from '@/features/auth/RegisterPage'
import { ForgotPasswordPage, ResetPasswordPage, VerifyEmailPage } from '@/features/auth/AccountRecoveryPages'
import { ProtectedRoute } from './ProtectedRoute'
import { FounderWorkspaceRoute } from './FounderWorkspaceRoute'
import { LandingPage } from '@/pages/LandingPage'
import { DashboardPage } from '@/features/dashboard/DashboardPage'
import { StartupSubmissionPage } from '@/features/projects/StartupSubmissionPage'
import { EvaluationResultsPage } from '@/features/evaluations/EvaluationResultsPage'
import { ChatPage } from '@/features/chat/ChatPage'
import { AdminPage } from '@/features/admin/AdminPage'
import { ValidateLandingPage } from '@/pages/ValidateLandingPage'
import { StartupIdeaGeneratorPage } from '@/features/tools/StartupIdeaGeneratorPage'
import { LearnPage } from '@/pages/LearnPage'
import { ToolsDirectoryPage } from '@/pages/ToolsDirectoryPage'
import { PricingPage } from '@/pages/PricingPage'
import { AboutPage } from '@/pages/AboutPage'
import { ContactPage } from '@/pages/ContactPage'
import { LaunchGrowthPage } from '@/pages/LaunchGrowthPage'
import { FaqPage } from '@/pages/FaqPage'
import { ResourcePage } from '@/pages/ResourcePages'
import { CalculatorPage, CalculatorsDirectoryPage } from '@/pages/CalculatorsPage'
import { TemplatesPage } from '@/pages/TemplatesPage'
import { StartupStoriesPage } from '@/pages/StartupStoriesPage'
import { StartupBooksPage } from '@/pages/StartupBooksPage'
import { StartupLifecyclePage } from '@/features/lifecycle/StartupLifecyclePage'
import { HiringManagementPage } from '@/pages/HiringManagementPage'
import { PosterGeneratorPage } from '@/pages/PosterGeneratorPage'
import { BusinessOperationsPage } from '@/pages/BusinessOperationsPage'
import { BusinessAdvisorPage } from '@/pages/BusinessAdvisorPage'
import { HumanAdvisorsPage } from '@/pages/HumanAdvisorsPage'
import { AdvisorDashboardPage } from '@/pages/AdvisorDashboardPage'
import { AdvisorAvailabilityPage } from '@/pages/AdvisorAvailabilityPage'
import { FounderAppointmentsPage } from '@/pages/FounderAppointmentsPage'
import { AdvisorApplicationPage } from '@/pages/AdvisorApplicationPage'
import { AdvisorProfilePage } from '@/pages/AdvisorProfilePage'
import { BusinessRegistrationPage } from '@/pages/BusinessRegistrationPage'
import { PrivacyPage, TermsPage } from '@/pages/LegalPages'
import { KnowledgeHubPage } from '@/pages/KnowledgeHubPage'
import { FounderProfilePage } from '@/pages/FounderProfilePage'

export function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppShell />}>
          <Route index element={<LandingPage />} />
          <Route path="login" element={<LoginPage />} />
          <Route path="register" element={<RegisterPage />} />
          <Route path="forgot-password" element={<ForgotPasswordPage />} />
          <Route path="reset-password" element={<ResetPasswordPage />} />
          <Route path="verify-email" element={<VerifyEmailPage />} />
          <Route path="terms" element={<TermsPage />} />
          <Route path="privacy" element={<PrivacyPage />} />
          <Route path="validate" element={<ValidateLandingPage />} />
          <Route path="tools/startup-idea-generator" element={<StartupIdeaGeneratorPage />} />
          <Route path="idea-generator" element={<StartupIdeaGeneratorPage />} />
          <Route path="learn" element={<LearnPage />} />
          <Route path="knowledge-hub" element={<KnowledgeHubPage />} />
          <Route path="tools" element={<ToolsDirectoryPage />} />
          <Route path="pricing" element={<PricingPage />} />
          <Route path="about" element={<AboutPage />} />
          <Route path="contact" element={<ContactPage />} />
          <Route path="faq" element={<FaqPage />} />
          <Route path="research/competitor-comparisons" element={<ResourcePage type="competitors" />} />
          <Route path="research/failure-library" element={<ResourcePage type="failures" />} />
          <Route path="resources/templates" element={<TemplatesPage />} />
          <Route path="templates" element={<TemplatesPage />} />
          <Route path="stories" element={<StartupStoriesPage />} />
          <Route path="books" element={<StartupBooksPage />} />
          <Route path="resources/glossary" element={<ResourcePage type="glossary" />} />
          <Route path="explainable-ai" element={<ResourcePage type="explainable" />} />
          <Route path="calculators" element={<CalculatorsDirectoryPage />} />
          <Route path="calculators/startup-cost" element={<CalculatorPage kind="startup-cost" />} />
          <Route path="calculators/break-even" element={<CalculatorPage kind="break-even" />} />
          <Route path="calculators/runway" element={<CalculatorPage kind="runway" />} />
          <Route path="calculators/roi" element={<CalculatorPage kind="roi" />} />
          <Route path="calculators/cac" element={<CalculatorPage kind="cac" />} />
          <Route path="calculators/ltv" element={<CalculatorPage kind="ltv" />} />
          <Route path="calculators/market-size" element={<CalculatorPage kind="market-size" />} />
          <Route path="calculators/funding" element={<CalculatorPage kind="funding" />} />
          <Route path="calculators/equity-dilution" element={<CalculatorPage kind="equity-dilution" />} />
          <Route path="calculators/valuation" element={<CalculatorPage kind="valuation" />} />
          <Route element={<ProtectedRoute />}>
            <Route path="dashboard" element={<DashboardPage />} />
            <Route path="profile" element={<FounderProfilePage />} />
            <Route path="workspace" element={<StartupLifecyclePage />} />
            <Route path="registration" element={<BusinessRegistrationPage />} />
            <Route path="launch-growth" element={<LaunchGrowthPage />} />
            <Route path="hiring" element={<HiringManagementPage />} />
            <Route path="posters" element={<PosterGeneratorPage />} />
            <Route path="operations" element={<BusinessOperationsPage />} />
            <Route path="advisor" element={<BusinessAdvisorPage />} />
            <Route path="advisors" element={<HumanAdvisorsPage />} />
            <Route path="advisor-application" element={<AdvisorApplicationPage />} />
            <Route path="appointments" element={<FounderAppointmentsPage />} />
            <Route path="advisor-availability" element={<AdvisorAvailabilityPage />} />
            <Route path="advisor-dashboard" element={<AdvisorDashboardPage />} />
            <Route path="advisor-profile" element={<AdvisorProfilePage />} />
            <Route element={<FounderWorkspaceRoute />}>
              <Route path="projects/new" element={<StartupSubmissionPage />} />
            </Route>
            <Route path="projects/:projectId/evaluations/:evaluationId" element={<EvaluationResultsPage />} />
            <Route path="projects/:projectId/chat" element={<ChatPage />} />
            <Route path="admin" element={<AdminPage />} />
            <Route path="admin/advisor-approvals" element={<AdminPage section="advisors" />} />
            <Route path="admin/announcements" element={<AdminPage section="announcements" />} />
            <Route path="admin/users" element={<AdminPage section="users" />} />
            <Route path="admin/analytics" element={<AdminPage section="analytics" />} />
            <Route path="admin/feedback" element={<AdminPage section="feedback" />} />
          </Route>
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
