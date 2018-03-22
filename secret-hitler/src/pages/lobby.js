import * as React from 'react';
import Button from '../Componants/button';

export default class Lobby extends React.Component {
    constructor(props) {
      super(props);
      
      this.state = {
        data:this.props.data,
        socket:this.props.socket
      };
    }
    
    componentWillReceiveProps(nextProps){
      this.setState({data: nextProps.data})
      this.setState({socket: nextProps.socket})
    }

    render() {
      const { data } = this.state;
      //Start game button if is host
      //Display who is in the lobby
      // return <div>{this.state.data}</div>
      return <div>{data}</div>
    }
  }

