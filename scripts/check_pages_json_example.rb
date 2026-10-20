# Component regression for the exact Liquid syntax failure in Pages run 39116448448.
require 'liquid'

path = File.expand_path('../state/proposals/codex_scheduler_tests_proposal_2026-06-13.md', __dir__)
source = File.read(path, encoding: 'UTF-8').gsub("\r\n", "\n")
literal = 'Setup:  Write "NOT VALID JSON {{{" to MARKET_CACHE_FILE'
raise 'Corrupt JSON fixture unexpectedly changed' unless source.include?(literal)
raise 'Missing raw protection' unless source.include?("{% raw %}\n```\n#{literal}")
rendered = Liquid::Template.parse(source, error_mode: :strict).render!
raise 'Literal fixture lost during rendering' unless rendered.include?(literal)

unprotected = source.sub("{% raw %}\n", '').sub("{% endraw %}\n", '')
rejected = false
begin
  Liquid::Template.parse(unprotected, error_mode: :strict)
rescue Liquid::SyntaxError
  rejected = true
end
raise 'Negative control did not reproduce the original parser failure' unless rejected
puts "PAGES_LIQUID_EXAMPLE_CHECK=PASS liquid=#{Liquid::VERSION}; literal preserved; original rejected"
