import React from "react";
import "./SearchBar.css"
import SearchResult from "./SearchResult";

export default class SearchBar extends React.Component{
  constructor(props) {
    super(props);
    this.state = {
      company: {},
      nameOrurl: "",
    }
  }

  handleChange = event => {
    this.setState({ searchText: event.target.value});
  };

  search = event => {
    this.setState({nameOrurl: this.state.searchText});
    fetch('/search/' + this.state.searchText)
      .then(res => res.json())
      .then( data => {
        this.setState({
          company: data
        });
      }
    )
  };

  render() {
    let searchResult;

    if (!this.state.company || !this.state.company.name) {
      searchResult = <div> </div>
    }else if (!this.state.company.name || this.state.company.name === -1){
      //  The company does not exist in the database.
      searchResult = <div>We did not find {this.state.nameOrurl}! It's not in the database.</div>
    } else if (!this.state.company.twitter || this.state.company.twitter === -1) {
      searchResult = <div> We did not find a twitter account for {this.state.company.name}. </div>
    } else if (!this.state.company.nr_followers || this.state.company.nr_followers === -1) {
      searchResult = <div> We could not retrieve the number of followers for {this.state.company.name}. </div>
    } else if (!this.state.company.url || this.state.company.url === -1){
      searchResult = <div>Company name: {this.state.company.name} Nr. Followers: {this.state.company.nr_followers}
                          Twitter: {this.state.company.twitter}
                     </div>
    } else {
      searchResult = <SearchResult company={this.state.company} />
    }

    return (
      <div>
        <div className="component-search-bar">
            <input onChange={this.handleChange} />
            <br/>
            <button className="search-button" onClick={this.search}>Search</button>
        </div>
        <div className="search-result">
          {searchResult}
        </div>
      </div>
    );
  }

}