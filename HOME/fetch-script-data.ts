import { DOMParser } from "jsr:@b-fuze/deno-dom@^0.1.49";
import { Command } from "jsr:@cliffy/command@^1.0.0-rc.7";

await new Command()
  .name("fetch-script-data")
  .description("A CLI to fetch script data.")
  .version("v0.0.0")
  .arguments("<url> [filter]")
  .action(async ({ }, url, filter) => {
    filter ||= "id=__NEXT_DATA__";
    const resp = await fetch(url);
    const respText = await resp.text();

    const doc = new DOMParser().parseFromString(respText, "text/html");

    const nextData = doc.querySelector(`script[${filter}]`)!;
    console.log(nextData.innerText);
  })
  .parse();