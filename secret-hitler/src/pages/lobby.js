import * as React from 'react';
import Button from '../Componants/button';

export default class Lobby extends React.Component {
    constructor(props) {
      super(props);
      
      this.state = {
        data:this.props.data
      };
    }
    
    componentWillReceiveProps(nextProps){
      this.setState({data: nextProps.data})
    }

    render() {
      // const { data } = this.state;
      //Start game button if is host
      //Display who is in the lobby
      // return <div>{this.state.data}</div>
      return <div>{this.state.data['name']}</div>
      // return <Button caption="Join" onclick={() => {(alert("Player Joined"))}}/>;
    }
  }

