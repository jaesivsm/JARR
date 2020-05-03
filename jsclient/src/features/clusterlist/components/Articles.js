import React, { useState } from "react";

import Tab from "@material-ui/core/Tab";
import Tabs from "@material-ui/core/Tabs";

import Article from "./Article";
import makeStyles from "./style";
import ClusterIcon from "../../../components/ClusterIcon";

function Articles({ articles, icons }) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const classes = makeStyles();
  const isOnlyOneTitle = [...new Set(articles.map((a) => a.title))].length === 1;
  return (
    <>
      <Tabs indicatorColor="primary" textColor="primary"
        value={currentIndex}
        onChange={(e, v) => setCurrentIndex(v)}>
       {articles.map((article, index) => (
          <Tab key={`t-${index}`}
               className={classes.tabs}
               icon={<ClusterIcon iconUrl={icons[article["feed_id"]]} />}
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
