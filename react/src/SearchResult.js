import React from "react";
import "./SearchResult.css"

export default class SearchResult extends React.Component{

  render() {
    let company = this.props.company;
    return (
      <div className="component-search-result">
        <h1>{company.name}</h1>
        <p className="result-followers">Twitter followers: {company.nr_followers}</p>
        <div>
          <a href={company.url}>{company.url} </a>
        </div>
        <div>
          <a href={company.twitter}>{company.twitter}</a>
        </div>
      </div>
    );
  }

}