# SPARQL Templates

This directory contains SPARQL templates used for querying Wikidata to generate questions based on event data. The templates are designed to be flexible and can be adapted to various types of questions by replacing placeholders with actual entity values.

## Usage

To use a SPARQL template, replace the placeholders (e.g., `[ENTITY]`, `[RELATION]`) with actual values and execute the query using a SPARQL endpoint such as [Wikidata's Query Service](https://query.wikidata.org/).

### Example Template

```sparql
SELECT ?item ?itemLabel WHERE {
  ?item wdt:[RELATION] wd:[ENTITY].
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
}
```
### Contributing

If you have suggestions for new templates or improvements to existing ones, please submit a pull request or open an issue on the repository.

### Note

More templates will be added
