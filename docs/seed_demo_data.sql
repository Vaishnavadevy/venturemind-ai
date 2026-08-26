-- VentureMind AI: safe local demonstration data
-- Run this in phpMyAdmin after selecting the `venture` database.
-- It does NOT delete tables or existing user accounts.
-- It uses the existing user@gmail.com account from your exported database.

START TRANSACTION;

SET @founder_id = '18df7b5b-33a4-4fff-a1c1-219d37f8cd19';
SET @org_id = '11111111-1111-4111-8111-111111111111';
SET @profile_id = '22222222-2222-4222-8222-222222222222';
SET @project_id = '33333333-3333-4333-8333-333333333333';
SET @idea_id = '44444444-4444-4444-8444-444444444444';
SET @evaluation_id = '55555555-5555-4555-8555-555555555555';
SET @employee_one = '66666666-6666-4666-8666-666666666661';
SET @employee_two = '66666666-6666-4666-8666-666666666662';

INSERT INTO organizations (id, owner_id, name, country, created_at, updated_at)
VALUES (@org_id, @founder_id, 'Northern Harvest Foods', 'Sri Lanka', '2026-07-25 09:00:00', '2026-07-25 09:00:00')
ON DUPLICATE KEY UPDATE name = VALUES(name), country = VALUES(country), updated_at = VALUES(updated_at);

INSERT INTO organization_members (id, organization_id, user_id, member_role, created_at, updated_at)
VALUES ('11111111-1111-4111-8111-111111111112', @org_id, @founder_id, 'founder', '2026-07-25 09:00:00', '2026-07-25 09:00:00')
ON DUPLICATE KEY UPDATE member_role = VALUES(member_role), updated_at = VALUES(updated_at);

INSERT INTO startup_profiles (id, organization_id, created_by_id, business_name, category, industry, description, target_customers, country, district, city, expected_investment, available_budget, business_experience, business_goals, business_size, startup_type, partner_count, expected_employees, launch_timeline, status, created_at, updated_at)
VALUES (@profile_id, @org_id, @founder_id, 'Northern Harvest Foods', 'Food and beverage', 'Healthy food retail', 'A Jaffna-based prepared-food and healthy grocery venture that combines fresh local ingredients with pre-order delivery.', 'Working professionals, students, and health-conscious families in Jaffna.', 'Sri Lanka', 'Jaffna', 'Jaffna', 1800000.00, 1250000.00, 'Founder has experience in food preparation and customer service.', 'Validate demand, launch a small MVP outlet, and reach positive monthly cash flow within 12 months.', 'small', 'new venture', 2, 5, 'Launch MVP within 4 months', 'active', '2026-07-25 09:10:00', '2026-07-30 10:00:00')
ON DUPLICATE KEY UPDATE description = VALUES(description), target_customers = VALUES(target_customers), expected_investment = VALUES(expected_investment), available_budget = VALUES(available_budget), status = VALUES(status), updated_at = VALUES(updated_at);

INSERT INTO lifecycle_milestones (id, startup_profile_id, milestone_key, title, weight, completed_at, created_at, updated_at) VALUES
('71000000-0000-4000-8000-000000000001', @profile_id, 'idea_created', 'Business idea defined', 10, '2026-07-25 09:10:00', '2026-07-25 09:10:00', '2026-07-25 09:10:00'),
('71000000-0000-4000-8000-000000000002', @profile_id, 'risk_analysis', 'Risk analysis completed', 10, '2026-07-30 10:00:00', '2026-07-30 10:00:00', '2026-07-30 10:00:00'),
('71000000-0000-4000-8000-000000000003', @profile_id, 'market_research', 'Interview target customers', 10, NULL, '2026-07-30 10:00:00', '2026-07-30 10:00:00'),
('71000000-0000-4000-8000-000000000004', @profile_id, 'mvp', 'Launch MVP menu', 10, NULL, '2026-07-30 10:00:00', '2026-07-30 10:00:00')
ON DUPLICATE KEY UPDATE completed_at = VALUES(completed_at), updated_at = VALUES(updated_at);

INSERT INTO lifecycle_risk_assessments (id, startup_profile_id, overall_success_score, business_confidence_score, overall_risk_score, risk_level, methodology_version, scorecards, recommendations, created_at, updated_at)
VALUES ('72000000-0000-4000-8000-000000000001', @profile_id, 68.00, 72.00, 41.00, 'moderate', 'rules-v1',
JSON_ARRAY(JSON_OBJECT('category','Market risk','score',45,'reasoning','Local demand still needs customer interviews.'), JSON_OBJECT('category','Financial risk','score',38,'reasoning','Budget covers an MVP but requires weekly cash-flow tracking.'), JSON_OBJECT('category','Operational risk','score',40,'reasoning','Supplier and food-safety processes need documentation.')),
JSON_ARRAY(JSON_OBJECT('priority','high','action','Interview 15 target customers before finalising the menu.'), JSON_OBJECT('priority','medium','action','Track food cost, wastage, and daily sales from the first week.')),
'2026-07-30 10:00:00', '2026-07-30 10:00:00')
ON DUPLICATE KEY UPDATE overall_success_score = VALUES(overall_success_score), business_confidence_score = VALUES(business_confidence_score), overall_risk_score = VALUES(overall_risk_score), scorecards = VALUES(scorecards), recommendations = VALUES(recommendations), updated_at = VALUES(updated_at);

INSERT INTO lifecycle_financial_plans (id, startup_profile_id, assumptions, results, created_at, updated_at)
VALUES ('73000000-0000-4000-8000-000000000001', @profile_id,
JSON_OBJECT('monthly_revenue',450000,'monthly_fixed_costs',210000,'monthly_variable_costs',110000,'initial_investment',1250000),
JSON_OBJECT('monthly_profit',130000,'break_even_months',10,'estimated_runway_months',8,'roi_percent',42),
'2026-07-30 10:05:00', '2026-07-30 10:05:00')
ON DUPLICATE KEY UPDATE assumptions = VALUES(assumptions), results = VALUES(results), updated_at = VALUES(updated_at);

INSERT INTO projects (id, owner_id, name, description, status, created_at, updated_at)
VALUES (@project_id, @founder_id, 'Northern Harvest Foods', 'Healthy prepared food and grocery venture for Jaffna.', 'ACTIVE', '2026-07-28 09:00:00', '2026-07-30 10:10:00')
ON DUPLICATE KEY UPDATE name = VALUES(name), description = VALUES(description), status = VALUES(status), updated_at = VALUES(updated_at);

INSERT INTO startup_ideas (id, project_id, version, startup_name, industry, country, target_audience, problem_statement, proposed_solution, business_model, revenue_model, development_stage, budget_amount, budget_currency, competitors, additional_notes, created_at, updated_at)
VALUES (@idea_id, @project_id, 1, 'Northern Harvest Foods', 'Food and beverage', 'Sri Lanka', 'Jaffna working professionals, students, and health-conscious families.', 'Customers need convenient, trustworthy healthy meals using local ingredients.', 'Pre-order meal boxes and selected healthy groceries with pickup and local delivery.', 'Direct-to-customer food retail with pre-orders.', 'Per-meal sales, subscriptions, and delivery charges.', 'MVP', 1250000.00, 'LKR', JSON_ARRAY(), 'Seeded local demonstration record.', '2026-07-28 09:05:00', '2026-07-30 10:10:00')
ON DUPLICATE KEY UPDATE industry = VALUES(industry), target_audience = VALUES(target_audience), proposed_solution = VALUES(proposed_solution), updated_at = VALUES(updated_at);

INSERT INTO evaluations (id, project_id, startup_idea_id, status, pipeline_version, overall_confidence_score, structured_extraction, swot_analysis, business_model_canvas, market_analysis, competitor_analysis, risk_analysis, investment_readiness, roadmap, financial_forecast, recommendations, llm_model, input_tokens, output_tokens, completed_at, failure_reason, created_at, updated_at)
VALUES (@evaluation_id, @project_id, @idea_id, 'COMPLETED', 'v1.0', 72.00,
JSON_OBJECT('industry','Food and beverage','keywords',JSON_ARRAY('healthy meals','Jaffna','pre-order')),
JSON_OBJECT('strengths',JSON_ARRAY('Clear local customer segment','Founder domain experience'),'weaknesses',JSON_ARRAY('Demand evidence is still limited'),'opportunities',JSON_ARRAY('Growing demand for convenient healthy meals'),'threats',JSON_ARRAY('Local food competition and ingredient price changes')),
JSON_OBJECT('value_proposition','Convenient healthy meals using trusted local ingredients','customer_segments','Jaffna professionals and families','channels','Pre-order website, WhatsApp, local delivery','revenue_streams','Meal sales and subscriptions'),
JSON_OBJECT('demand','Promising but requires interviews','growth_potential','Moderate'), JSON_ARRAY(), JSON_OBJECT('level','moderate','risk_resilience_score',59,'note','Risk context reflects recorded market, financial, and operational evidence.'), JSON_OBJECT('score',65,'stage','pre-seed'), JSON_ARRAY(JSON_OBJECT('phase','Research','milestone','Interview 15 customers','outcome','Validated customer evidence'),JSON_OBJECT('phase','MVP','milestone','Launch a limited menu','outcome','First repeat customers')), JSON_OBJECT('monthly_revenue',450000,'monthly_expenses',320000,'break_even_months',10), JSON_ARRAY(JSON_OBJECT('metric','pricing','recommendation','Test three meal price points with target customers.')), 'seeded-local-data', 1240, 680, '2026-07-30 10:10:00', NULL, '2026-07-28 09:10:00', '2026-07-30 10:10:00')
ON DUPLICATE KEY UPDATE status = VALUES(status), overall_confidence_score = VALUES(overall_confidence_score), input_tokens = VALUES(input_tokens), output_tokens = VALUES(output_tokens), updated_at = VALUES(updated_at);

INSERT INTO evaluation_scores (id, evaluation_id, metric_key, score, weight, reasoning, positive_factors, negative_factors, improvement_suggestions, factor_breakdown, created_at, updated_at) VALUES
('74000000-0000-4000-8000-000000000001', @evaluation_id, 'market_opportunity', 70.00, 0.2000, 'Local convenience demand is plausible but needs direct validation.', JSON_ARRAY('Defined location and customer group'), JSON_ARRAY('No interview evidence recorded'), JSON_ARRAY('Interview 15 target customers'), JSON_OBJECT('demand_signal',70), '2026-07-30 10:10:00', '2026-07-30 10:10:00'),
('74000000-0000-4000-8000-000000000002', @evaluation_id, 'business_model', 74.00, 0.2000, 'Direct sales and subscriptions provide clear revenue routes.', JSON_ARRAY('Multiple revenue options'), JSON_ARRAY('Pricing is untested'), JSON_ARRAY('Run a pricing test'), JSON_OBJECT('revenue_clarity',74), '2026-07-30 10:10:00', '2026-07-30 10:10:00'),
('74000000-0000-4000-8000-000000000003', @evaluation_id, 'scalability', 68.00, 0.2000, 'Pre-orders can scale after operating processes are standardised.', JSON_ARRAY('Pre-order model'), JSON_ARRAY('Supplier process not documented'), JSON_ARRAY('Document kitchen and supplier SOPs'), JSON_OBJECT('process_readiness',68), '2026-07-30 10:10:00', '2026-07-30 10:10:00')
ON DUPLICATE KEY UPDATE score = VALUES(score), reasoning = VALUES(reasoning), updated_at = VALUES(updated_at);

INSERT INTO employees (id, startup_profile_id, full_name, job_title, employment_status, created_at, updated_at) VALUES
(@employee_one, @profile_id, 'Kavitha S.', 'Kitchen Assistant', 'active', '2026-07-30 10:20:00', '2026-07-30 10:20:00'),
(@employee_two, @profile_id, 'Arun K.', 'Delivery Coordinator', 'active', '2026-07-30 10:20:00', '2026-07-30 10:20:00')
ON DUPLICATE KEY UPDATE job_title = VALUES(job_title), employment_status = VALUES(employment_status), updated_at = VALUES(updated_at);

INSERT INTO attendance_records (id, employee_id, attendance_date, status, created_at, updated_at) VALUES
('75000000-0000-4000-8000-000000000001', @employee_one, CURDATE(), 'present', NOW(), NOW()),
('75000000-0000-4000-8000-000000000002', @employee_two, CURDATE(), 'present', NOW(), NOW())
ON DUPLICATE KEY UPDATE status = VALUES(status), updated_at = VALUES(updated_at);

INSERT INTO operation_tasks (id, startup_profile_id, title, assigned_employee_id, status, created_at, updated_at) VALUES
('76000000-0000-4000-8000-000000000001', @profile_id, 'Confirm weekly vegetable supplier prices', @employee_one, 'todo', '2026-07-30 10:20:00', '2026-07-30 10:20:00'),
('76000000-0000-4000-8000-000000000002', @profile_id, 'Test delivery route for Jaffna town orders', @employee_two, 'in_progress', '2026-07-30 10:20:00', '2026-07-30 10:20:00')
ON DUPLICATE KEY UPDATE title = VALUES(title), assigned_employee_id = VALUES(assigned_employee_id), status = VALUES(status), updated_at = VALUES(updated_at);

INSERT INTO announcements (id, startup_profile_id, message, created_at, updated_at)
VALUES ('77000000-0000-4000-8000-000000000001', @profile_id, 'Trial meal-preparation day is scheduled for Friday. Please confirm ingredient availability by Thursday.', '2026-07-30 10:25:00', '2026-07-30 10:25:00')
ON DUPLICATE KEY UPDATE message = VALUES(message), updated_at = VALUES(updated_at);

INSERT INTO feedback (id, user_id, category, message, rating, status, admin_note, created_at, updated_at) VALUES
('78000000-0000-4000-8000-000000000001', @founder_id, 'Risk analysis', 'The risk analysis was useful. Please add more food-industry examples for Sri Lanka.', 4, 'OPEN', NULL, '2026-07-30 11:00:00', '2026-07-30 11:00:00'),
('78000000-0000-4000-8000-000000000002', @founder_id, 'Business operations', 'A supplier and inventory planning section would be helpful for a food startup.', 5, 'IN_REVIEW', 'Planned for the next operations module.', '2026-07-31 09:30:00', '2026-07-31 09:30:00')
ON DUPLICATE KEY UPDATE message = VALUES(message), rating = VALUES(rating), status = VALUES(status), admin_note = VALUES(admin_note), updated_at = VALUES(updated_at);

INSERT INTO notifications (id, user_id, notification_type, title, body, payload, is_read, read_at, created_at, updated_at) VALUES
('79000000-0000-4000-8000-000000000001', @founder_id, 'evaluation_ready', 'Evaluation completed', 'Your Northern Harvest Foods evaluation is ready to review.', JSON_OBJECT('project_id', @project_id, 'evaluation_id', @evaluation_id), 0, NULL, '2026-07-30 10:10:00', '2026-07-30 10:10:00')
ON DUPLICATE KEY UPDATE title = VALUES(title), body = VALUES(body), is_read = VALUES(is_read), updated_at = VALUES(updated_at);

COMMIT;
