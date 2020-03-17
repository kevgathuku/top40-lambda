# UK Top 40 Singles Chart API

Provides [The Official UK Top 40 Singles Chart](https://www.bbc.co.uk/radio1/chart/singles/) as a JSON API.

Replacement of the no-longer-available
[Ben Major UK Top 40 API](https://web.archive.org/web/20140418084450/http://ben-major.co.uk/labs/top40/api/singles)
and alternative to the [PythonTop40Server](https://pythontop40server.herokuapp.com)

Powered by:

- [Python 3](https://www.python.org/)
- [Chalice](https://github.com/awslabs/chalice)
- [PythonTop40Server](https://bitbucket.org/dannygoodall/pythontop40server)
- [AWS Lambda](https://aws.amazon.com/lambda/)

## Quickstart

Make an HTTP get request to [the singles API endpoint](https://htpkwhl59f.execute-api.eu-central-1.amazonaws.com/api/singles) to get the current charts in JSON format.

#### Example:

```sh
pip install httpie
```

```
http https://wckb0ftk67.execute-api.eu-west-1.amazonaws.com/dev/singles
```

Sample Response:

```json
 "date": 1477612800,
 "retrieved": 1477750015,
 "entries": [
   {
     "status": "NON MOVER",
     "artist": "Little Mix",
     "title": "Shout Out To My Ex",
     "previousPosition": 1,
     "position": 1,
     "numWeeks": 2,
     "change": {
       "amount": 0,
       "actual": 0,
       "direction": "none"
     }
   },
 ]
```

### Response Data Format:

```json
{
  "date": "Date the Charts were Released",
  "retrieved": "Current Date",
  "Entries": "Array of singles in the current Charts"
}
```

## Data Source

[The Official UK Top 40 Singles Chart](https://www.bbc.co.uk/radio1/chart/singles/print)
