-- Migration: Import Lookup Data
-- Created: 2025-04-09

-- Import status types
INSERT INTO status_types (status, description, aliases) VALUES
('Active', 'Currently airing or in production', ARRAY['Running', 'Current', 'In Production']),
('Ended', 'Completed as planned', ARRAY['Finished', 'Complete', 'Series End']),
('Cancelled', 'Terminated before planned end', ARRAY['Axed', 'Discontinued', 'Not Renewed']),
('Development', 'In pre-production phase', ARRAY['In Development', 'Pre-Production']),
('Announced', 'Officially announced but not started', ARRAY['Greenlit', 'Ordered']),
('Pilot', 'Pilot ordered or in production', ARRAY['Pilot Order', 'Test Episode']);

-- Import network_list
INSERT INTO network_list (network, type, parent_company, aliases) VALUES
('ABC', 'Broadcast', 'Disney', ARRAY['ABC Network', 'American Broadcasting Company']),
('AMC', 'Cable', 'AMC Networks', ARRAY['AMC+', 'AMC Plus']),
('Apple TV+', 'Streamer', 'Apple', ARRAY['Apple', 'Apple TV', 'Apple+', 'Apple Original', 'Apple TV Plus']),
('Blackpills', 'Digital', 'Blackpills SAS', ARRAY['Blackpills', 'BlackPills', 'Black Pills']),
('Canal Plus', 'Premium', 'Vivendi (Canal Group)', ARRAY['Canal+', 'Canal Plus', 'CANAL+', 'Canal Plus Group', 'StudioCanal']),
('CBS', 'Broadcast', 'Paramount', ARRAY['CBS Network', 'Columbia Broadcasting']),
('Disney+', 'Streamer', 'Disney', ARRAY['Disney Plus', 'D+', 'Disney Original']),
('Epix', 'Premium', 'MGM', ARRAY['EPIX', 'MGM+']),
('Fox', 'Broadcast', 'Fox', ARRAY['FOX Network', 'Fox Broadcasting']),
('FX', 'Cable', 'Disney', ARRAY['FX', 'FX Network', 'FX on Hulu', 'FX Original']),
('HBO', 'Premium', 'Warner Bros Discovery', ARRAY['HBO Max', 'HBOMax', 'Max', 'HBO Original']),
('Hulu', 'Streamer', 'Disney', ARRAY['Hulu Original', 'Hulu+']),
('NBC', 'Broadcast', 'NBCU', ARRAY['NBC Network', 'National Broadcasting']),
('Netflix', 'Streamer', 'Netflix', ARRAY['NFLX', 'Netflix+']),
('Paramount+', 'Streamer', 'Paramount', ARRAY['Paramount Plus', 'P+']),
('Peacock', 'Streamer', 'NBCU', ARRAY['Peacock Original', 'Peacock+']),
('Prime Video', 'Streamer', 'Amazon', ARRAY['Amazon', 'Amazon Prime', 'Prime Video', 'Amazon Prime Video', 'Amazon Original', 'Amazon Studios']),
('Showtime', 'Premium', 'Paramount', ARRAY['SHO', 'Showtime Original']),
('Starz', 'Premium', 'Lionsgate', ARRAY['STARZ']),
('TBS', 'Cable', 'Warner Bros Discovery', ARRAY['Turner Broadcasting']),
('TNT', 'Cable', 'Warner Bros Discovery', ARRAY['Turner Network Television']),
('USA', 'Cable', 'NBCU', ARRAY['USA Network', 'USA Original']),
('CW', 'Broadcast', 'Nexstar Media Group', ARRAY['CW', 'The CW', 'CW Network', 'The CW Network']),
('Tubi', 'Streamer', 'Fox', ARRAY['Tubi tv', 'Tubitv']),
('BET', 'Streamer', 'Black Entertainment Television', ARRAY['Paramount BET Plus', 'BET+']),
('Hallmark+', 'Cable', 'Crown Media', ARRAY['Hallmark Channel', 'Hallmark Media Hallmark', 'Hallmark+', 'Hallmark+ ']);

-- Import studio_list (abbreviated for readability, full list in actual data)
INSERT INTO studio_list (studio, type, parent_company, division, platform, aliases, category) VALUES
('20th Television', 'Studio', 'Disney', 'Disney Television Studios', 'Disney+', 
 ARRAY['20th Century TV', '20th Century Fox TV'], 
 ARRAY['Vertically Integrated', 'Network-First']),
('Warner Bros Television', 'Studio', 'Warner Bros Discovery', 'WB Television Group', 'Max',
 ARRAY['WBTV', 'Warner Bros. Television', 'Warner Bros. Television Studios', 'Warner Brothers Television', 'Warner Brothers Television Studios', 'WB Television Studios', 'WB TV Studios', 'Warner Bros. Studio', 'Warner Bros. TV'],
 ARRAY['Vertically Integrated', 'Network-First']),
('Universal Television', 'Studio', 'NBCU', 'NBCUniversal Television', 'Peacock',
 ARRAY['UTV'],
 ARRAY['Vertically Integrated', 'Network-First']),
('Netflix Studios', 'Studio', 'Netflix', NULL, 'Netflix',
 ARRAY['Netflix'],
 ARRAY['Vertically Integrated', 'Streaming-First']),
('Other', 'Studio', 'Other', NULL, NULL,
 ARRAY[]::text[],
 ARRAY['Other']);

-- Import genre_list
INSERT INTO genre_list (genre, category, aliases) VALUES
('Action & Adventure', 'Main', ARRAY['Action', 'Adventure', 'Action-Adventure', 'Adventure Series']),
('Animation', 'Main', ARRAY['Animated', 'Cartoon', 'Animated Series']),
('Comedy', 'Main', ARRAY['Com', 'Comedy Series', 'Sitcom']),
('Crime', 'Main', ARRAY['Crime Drama', 'Police', 'Detective', 'Procedural']),
('Documentary', 'Main', ARRAY['Doc', 'Non-Fiction', 'Documentary Series']),
('Drama', 'Main', ARRAY['Dramatic Series', 'Character Drama']),
('Family', 'Main', ARRAY['Kids Show', 'Children', 'Family Series']),
('Kids', 'Main', ARRAY['Children''s', 'Youth', 'Kids Series']),
('Mystery', 'Main', ARRAY['Detective', 'Suspense', 'Mystery Series']),
('News', 'Main', ARRAY['News Program', 'Current Affairs', 'Newscast']),
('Reality', 'Main', ARRAY['Reality TV', 'Unscripted', 'Real Life']),
('Sci-Fi & Fantasy', 'Main', ARRAY['Science Fiction', 'Fantasy', 'SF', 'Speculative Fiction']),
('Soap', 'Main', ARRAY['Soap Opera', 'Daytime Drama', 'Telenovela']),
('Talk', 'Main', ARRAY['Talk Show', 'Chat Show', 'Interview Series']),
('War & Politics', 'Main', ARRAY['Political', 'War Drama', 'Military']),
('Western', 'Main', ARRAY['Old West', 'Cowboy', 'Western Drama']);

-- Import subgenre_list (same as genres for now)
INSERT INTO subgenre_list (subgenre, category, aliases)
SELECT genre, category, aliases FROM genre_list;

-- Import source_types
INSERT INTO source_types (type, category, aliases) VALUES
('Original', 'Original', ARRAY['New IP', 'Original Content']),
('Book', 'Literary', ARRAY['Novel', 'Fiction', 'Non-Fiction']),
('Short Story', 'Literary', ARRAY['Story', 'Novella']),
('Comic', 'Graphic', ARRAY['Comic Book', 'Graphic Novel']),
('Manga', 'Graphic', ARRAY['Japanese Comic']),
('Webtoon', 'Graphic', ARRAY['Web Comic', 'Digital Comic']),
('Film', 'Adaptation', ARRAY['Movie', 'Feature Film']),
('TV Show', 'Adaptation', ARRAY['Television Series', 'TV Series']),
('Game', 'Adaptation', ARRAY['Video Game', 'Mobile Game']),
('Podcast', 'Adaptation', ARRAY['Audio Series', 'Audio Show']),
('True Story', 'Real Events', ARRAY['Biography', 'Real Life Event']),
('News Story', 'Real Events', ARRAY['Current Events', 'News Adaptation']),
('Article', 'Real Events', ARRAY['Magazine Story', 'News Article']),
('Other', NULL, ARRAY[]::text[]),
('Toy', NULL, ARRAY['Toy line', 'ActionFigure', 'Toy IP']);

-- Import role_types
INSERT INTO role_types (role, category, aliases) VALUES
('Creator', 'Creative', ARRAY['c', 'Created By', 'Creator/EP']),
('Writer', 'Creative', ARRAY['w', 'Written By', 'Screenwrighter']),
('Director', 'Creative', ARRAY['d', 'Directed By']),
('Showrunner', 'Creative', ARRAY['sr', 'Show Runner']),
('Executive Producer', 'Production', ARRAY['ep', 'Exec Producer']),
('Producer', 'Production', ARRAY['p', 'Producer']),
('Co-Producer', 'Production', ARRAY['Co-EP', 'Associate Producer', 'coep', 'co ep', 'co-p']),
('Line Producer', 'Production', ARRAY['Line-P']),
('Studio Executive', 'Development', ARRAY['Studio Exec', 'Studio Rep']),
('Network Executive', 'Development', ARRAY['Network Exec', 'Network Rep']),
('Development Executive', 'Development', ARRAY['Dev Exec', 'Development Rep']),
('Actor', 'Talent', ARRAY['Star', 'Lead', 'Cast']),
('Host', 'Talent', ARRAY['Presenter', 'MC']),
('Co-Showrunner', 'Creative', ARRAY['co-sr']),
('Writer/Executive Producer', 'Creative', ARRAY['wep']),
('Creative Producer', 'Creative', ARRAY['cp']);

-- Import order_types
INSERT INTO order_types (type, description, aliases) VALUES
('Limited', 'One-season only, planned ending', ARRAY['Limited Series', 'Mini-Series', 'Event Series']),
('Ongoing', 'Multiple seasons possible', ARRAY['Series', 'Regular Series', 'Continuing Series']),
('Miniseries', 'Short run, typically 4-8 episodes', ARRAY['Mini Series', 'Limited Event']),
('Anthology', 'Each season different story/cast', ARRAY['Anthology Series', 'Season Anthology']),
('Pilot', 'Initial test episode', ARRAY['Pilot Order', 'Pilot Commitment']);
