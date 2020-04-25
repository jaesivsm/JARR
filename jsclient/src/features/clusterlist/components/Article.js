import React from "react";
import Typography from "@material-ui/core/Typography";

export default function Article({ link, comments, content, hidden }) {
  return (
    <Typography
       hidden={!!hidden}
       dangerouslySetInnerHTML={{__html: content}}
    />
  );
}
