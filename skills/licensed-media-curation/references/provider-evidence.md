# Provider evidence without provider folklore

Field names below are inspection hints, not a tested adapter contract. Confirm the current public API, source page and task validator.
Do not invent a helper, numeric license mapping or historical grant response.

## Wikimedia Commons

- Inspect image metadata, current full wikitext, source/author, licensing, warnings,
  credit, attribution, restrictions and binary-edit comments.
- Description revisions and binary upload history are different streams. Preserve
  required fields and all pagination when the contract needs complete histories;
  otherwise label the archive's actual bounded coverage.
- Requesting a nominal maximum is not proof of completeness. Follow the returned
  continuation object and dedupe by stable page/title while retaining populated
  metadata across partial responses.
- A description oldid does not pin the binary. Compare acquired bytes against the
  selected binary revision digest and timestamp; verify source hash encoding
  before comparison, retaining local SHA256 independently.
- Current self/Own work templates do not erase transfers, upstream credits or
  contrary history. A creator may have directly uploaded the work even if another
  site also mirrors it; establish direction rather than assuming import.
- A current correction can contradict a stale filename. Preserve rename/correction
  evidence instead of letting title substring matching overrule it.
- Expanded/transcluded templates can contain rights-bearing notices. Resolve
  relevant template redirects and public permission-request links. Distinct URLs
  need distinct cache paths; review aids that omit categories are not full archives.
- Older positional review templates, license aliases and mixed-type metadata values
  need deliberate parsing. A broad 'bot reviewed' substring is not photo-specific proof.

Official entry points: [image information](https://www.mediawiki.org/wiki/API:Imageinfo)
and [page revisions](https://www.mediawiki.org/wiki/API:Revisions).

## Flickr and imported copies

- Verify photo ID, owner/credit, photo page, exact per-photo grant and versioned
  license URL. Enumerate current provider license definitions when using numeric
  IDs; do not copy a static ID table from an old task.
- HTML evidence may place ImageObject inside JSON-LD `@graph`. Structured public
  data can corroborate a visible license, but only if bound to this exact image.
- Parse JSON as data. A JSON decoder's bounded raw-decode operation can extract
  a JSON object from surrounding text; never evaluate page JavaScript.
- Historical photo-specific bot reviews may be evidence but do not supply a missing
  primary grant response by themselves. General bot documentation is not a grant.
- Compare upstream and imported binaries when the consumer requires equality.
  A larger original and a resized import can depict the same scene with different
  bytes; record the precise failing gate rather than a universal rights verdict.
- Posted, taken and updated timestamps are not complete license/revision histories.
- Account biographies can contain additional credit or identity cautions, but must
  not be converted into new permissions or personal public dossiers.

## iNaturalist

- Treat taxon-name searches as discovery; verify exact returned identity and rank.
- Bind the observation, chosen photo ID, photo association, supplied attribution,
  dimensions and moderation/hidden/flag state. Inspect every relevant attached
  photo; first/last-photo sampling is not exhaustive review.
- Observation or dataset licensing is not the photograph's grant. Generic license
  codes may omit version: retain the exact photo-specific URL/version evidence.
- Some public representations expose association-nested photo objects rather than
  a top-level photo list. Confirm the current response shape.
- LocalPhoto labels alone do not establish native origin. External native-page,
  original-URL, username or subtype pointers require upstream-chain review.
- A user profile, observer, supplied photo credit and authenticated creator account
  are distinct assertions. Do not infer numeric ownership without evidence.
- A guessed filter that returns unrelated/global results is malformed evidence,
  not a supported lookup and not a botanical negative.

Consult the [official API documentation](https://api.inaturalist.org/v1/docs/).
Legacy-source representations require current independent validation.

## GBIF, specimen and institutional aggregators

- Verify exact taxon keys before occurrence discovery. Fuzzy name queries can return
  broader concepts. Preserve authored names, rank and original source assertions.
- Inspect basis of record and media type. A preserved sheet is not a living habit photo.
- Dataset/occurrence license, aggregator-normalized convenience license and
  media-level grant can disagree. Inspect literal media rights and linked source.
- Record photographer credit as supplied. Collectors and determiners are not
  automatically photographers. An accession identifies material, not photo ownership.
- Institution logos, public downloads and missing EXIF copyright are not permission.
- Specimen evidence may be valuable when permitted; never silently substitute it
  where the user requires living material or the exact qualified source concept.

Start at [GBIF developer documentation](https://techdocs.gbif.org/en/openapi/).
A useful source can remain unsupported by a project's adapter without being
unlicensed or unusable in every other context.
