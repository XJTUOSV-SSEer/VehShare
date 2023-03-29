pragma solidity >=0.4.22 <0.8.0;

contract write {
    mapping(bytes32 => bytes32) public edb; //定长字节数组大小不确定
    mapping(bytes32 => uint256) public edb1;
    bytes32 []  public mei;
    mapping(bytes32 => bytes32[])  public st;
    mapping(bytes32 => uint256) public c;
    mapping(bytes32 => uint256) public st2int;

    // function set_st(bytes32 add,uint256 val) public{
    //     st2int[add]=val;
    // } 
    function batch_stint(uint batch,bytes32[] add,uint256[] val) public{
        for(uint i = 0;i<batch;i++){
            bytes32 x = add[i];
            uint256 y = val[i];
            st2int[x] = y;
        }
    }

    // //test
    // bytes32 hashhex;
    // uint256 public hexnum;
    // bytes32 res;

    // function set_hashhex(bytes32 add) public{//memory?
    //     hashhex = add;
    // }

    // function set_hexnum(uint256 add) public{//memory?
    //     hexnum = add;
    // }

    // function retrieve1() public view returns(bytes32){
    //     return hashhex;
    // }

    // function retrieve2() public view returns(bytes32){
    //     bytes32 temp = keccak256(abi.encodePacked(hexnum+1));
    //     return temp;
    // }


    //bytes32 mei = bytes32(0x0);
    bytes32 st_1;
    bytes32 add_st;
    bytes32 val_tw;
    //传入EDB里值的函数
    // function set_edb(bytes32 add, bytes32 val) public{//memory?
    //     edb[add]=val;
    // } 
    function batch_ind(uint batch,bytes32[] add,bytes32[] val) public{
        for(uint i = 0;i<batch;i++){
            bytes32 x = add[i];
            bytes32 y = val[i];
            edb[x] = y;
        }
    }   
    function batch_tw(uint batch,bytes32[] add,bytes32[] val) public{
        for(uint i = 0;i<batch;i++){
            bytes32 x = add[i];
            bytes32 y = val[i];
            edb[x] = y;
        }
    }  



    // function set_edb1(bytes32 add,uint256 val) public{//memory?
    //     edb1[add]=val;
    // } 
    function batch_st(uint batch,bytes32[] add,uint256[] val) public{
        for(uint i = 0;i<batch;i++){
            bytes32 x = add[i];
            uint256 y = val[i];
            edb1[x] = y;
        }
    }

    // function set_st1(bytes32 w,bytes32 val) public{//memory?
    //     st[w].push(val);
    //     if(st[w].length == 1){
    //         c[w] = 0;
    //     }
    //     c[w]++;
    // } 
    function batch_st1(uint batch,bytes32[] add,bytes32[] val) public{
        for(uint i = 0;i<batch;i++){
            bytes32 x = add[i];
            bytes32 y = val[i];
            st[x].push(y);
            if(st[x].length == 1){
                c[x] = 0;
            }
            c[x]++;
        }
    }

    //
    function search(bytes32 w,bytes32 tw) public {
        uint i = c[w]-1;
        bytes32 add_tw = keccak256(abi.encodePacked(tw));//bytes32 -> bytes
        add_tw = tw;
        val_tw = edb[add_tw];
        st_1 =  val_tw ^ add_tw;
        add_st = keccak256(abi.encodePacked(st_1));
        while(edb1[add_st] != 0){//如何判断mapping为空

            uint256 val_st = edb1[add_st];
            //bytes32 mk = val_st ^ keccak256(abi.encodePacked(st_1));//mk 为 1||k
            //bytes16 j = bytes16(mk);
            // 1 - val_St
            uint256 stint = st2int[st_1];
            for(uint256 j = 1; j <= val_st;j++){
                bytes32 add_ind = keccak256(abi.encodePacked(stint+j));
                bytes32 val_ind = edb[add_ind];
                bytes32 EI = val_ind ^ keccak256(abi.encodePacked(stint+j));
                mei.push(EI);   
            }
            if(i==0){
                break;
            }else{
                st_1 = st[w][i-1];
                add_st = keccak256(abi.encodePacked(st_1));
                i--;
            }
        }

        

    }
    function retrieve0() public view returns(bytes32 [] memory){
        return mei;
    }

    // function retrieve1() public view returns(bytes32 [] memory){
    //     return st;
    // }

    // function retrieve1() public view returns(bytes32 ){
    //     return st_1;
    // }
    // function retrieve2() public view returns(bytes32 ){
    //     return val_tw;
    // }

}