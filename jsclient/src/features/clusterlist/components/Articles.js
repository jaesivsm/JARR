import React, { useState } from "react";

import Tab from "@material-ui/core/Tab";
import Tabs from "@material-ui/core/Tabs";

import Article from "./Article";
import makeStyles from "./articlesStyle";
import FeedIcon from "../../../components/FeedIcon";

function Articles({ articles, icons }) {
  const [currentIndex, setCurrentIndex] = useState(0)
  const classes = makeStyles();
  const isOnlyOneTitle = [...new Set(articles.map((a) => a.title))].length === 1;
    console.log(articles);
  return (
    <>
      <Tabs indicatorColor="primary" textColor="primary"
        value={currentIndex}
        onChange={(e, v) => setCurrentIndex(v)}>
       {articles.map((article, index) => (
          <Tab key={`t-${index}`}
               className={classes.tabs}
               icon={<FeedIcon iconUrl={icons[article["feed_id"]]} />}
               label={isOnlyOneTitle ? null : article.title}
               value={index}
               aria-controls={`a-${index}`}
           />
       ))}
      </Tabs>
      {articles.map((article, index) =>
         <Article
            key={`a-${index}-${index !== currentIndex ? "h" : ""}`}
            id={`a-${index}`}
            article={article}
            aria-labelledby={`t-${index}`}
            index={index}
            hidden={index !== currentIndex}
          />
      )}
    </>
  );
}
export default Articles;
