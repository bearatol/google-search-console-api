# Agent Playbook: Search Performance Analysis and Improvement

Use this playbook after authorization and property discovery. Select only the reports needed for the user's outcome, but complete enough analysis to support each conclusion with evidence.

## 1. Establish context

Inspect the website workspace before querying data:

- identify the canonical domain and important sections;
- identify the business model, conversion actions, and protected or high-value pages when available;
- read active project instructions;
- note whether the user requested analysis only, recommendations, or implementation.

Do not ask the user for information that can be established safely from the workspace or Search Console properties.

## 2. Select exact periods

Use completed Search Console data. Unless the user specifies dates:

- end the current period three days before today;
- use the latest 28 completed days for a focused diagnostic;
- compare them with the immediately preceding 28 days;
- use 90 days for broader context or sparse sites.

Calculate and state exact dates. Compare equal-length periods and note seasonality when it can materially affect the result.

## 3. Retrieve the minimum complete dataset

Start with current and previous overview totals, then retrieve the dimensions needed to explain the change:

1. current and previous summaries;
2. page reports for both periods;
3. query reports for both periods;
4. date reports when timing or a specific drop matters;
5. device reports when device behavior may explain the result;
6. combined `query,page` data when search intent, page competition, or cannibalization matters.

Use `--no-cache` only when fresh data is important. Preserve exact result paths so full data can be inspected without flooding the response.

## 4. Diagnose performance

Evaluate at least the patterns relevant to the request:

### Losses

- pages or queries with material click decline;
- impression decline that suggests lost demand, coverage, or visibility;
- stable impressions with falling CTR;
- stable impressions and CTR with worse average position;
- abrupt date-level changes that may align with releases, indexing problems, migrations, or external events.

Do not claim causation from correlation. Mark hypotheses and verify them against the site, release history, URL Inspection, or additional dimensions.

### Growth opportunities

- high-impression queries and pages in average positions 4–20;
- high-impression results with CTR below comparable results on the same site and at similar positions;
- pages gaining impressions but not clicks;
- queries with clear intent that the landing page does not satisfy well;
- important pages missing meaningful non-brand visibility.

Do not use a universal CTR benchmark. Compare within the site and account for query type, brand intent, position, device, and search features.

### Page competition

Use `query,page` data to find queries distributed across multiple pages. Distinguish healthy coverage from likely cannibalization. Treat it as a problem only when pages compete for the same intent and performance is fragmented or unstable.

### Index and technical signals

Use URL Inspection for a small set of priority URLs when the evidence suggests indexing, canonical, robots, crawl, or coverage problems. Do not inspect every URL without a reason.

## 5. Map evidence to actions

Connect each recommended change to a specific observed pattern:

- low CTR with stable visibility: review title, snippet promise, intent match, and competing result format;
- positions 4–20 with strong impressions: strengthen intent coverage, evidence, structure, and internal links;
- declining page visibility: compare content, technical state, cannibalization, and recent site changes;
- canonical or indexing mismatch: inspect templates, canonical tags, robots directives, redirects, and sitemap membership;
- device-specific weakness: inspect the affected layout, performance, and interaction path;
- competing pages: consolidate, differentiate intent, redirect, or adjust internal linking only after reviewing both pages.

Avoid generic advice such as “improve content” or “add keywords.” Specify the page, evidence, proposed change, expected mechanism, and validation metric.

## 6. Implement when requested

If the user asks the agent to improve or fix the site:

1. locate the relevant page and its source of truth in the current workspace;
2. inspect existing content, metadata, structured data, internal links, and technical directives;
3. prepare the plan required by the active project rules;
4. after approval, make only the changes supported by the evidence;
5. run the project's relevant tests, linting, formatting, builds, and route or SEO checks;
6. report changed files, validation results, and the Search Console metrics to monitor.

Search Console improvements are not immediate. Recommend a measurement window appropriate to the site's crawl frequency and traffic volume. Do not promise ranking gains.

## 7. Report the outcome

Use this structure when it helps clarity:

1. exact periods and property analyzed;
2. most important changes in clicks, impressions, CTR, and position;
3. diagnosed drivers with page and query evidence;
4. prioritized opportunities by expected impact and confidence;
5. changes implemented or an approval-ready plan;
6. validation and follow-up metrics.

Keep facts, interpretations, and recommendations distinct.
