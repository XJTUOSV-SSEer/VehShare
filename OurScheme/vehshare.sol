pragma solidity >=0.4.22 <=0.6.0;

contract write {
    ////////////////////////////
    mapping(bytes32 => bytes32) t_T;
    mapping(bytes32 => bytes32) t_f;
    mapping(bytes32 => bytes32) t_p;
    mapping(bytes32 => bytes32) l_v;
    mapping(bytes32 => bytes32) l_c;
    /////////////////////////////
    mapping(bytes32 => uint256) public N; 
    mapping(uint256 => bytes ) public AL; 
    bytes32 [] public  R ;
    
    int256[] public M;

    bytes32 public result1;
    bytes public pp = hex"90066455b5cfc38f9caa4a48b4281f292c260feef01fd61037e56258a7795a1c7ad46076982ce6bb956936c6ab4dcfe05e6784586940ca544b9b2140e1eb523f009d20a7e7880e4e5bfa690f1b9004a27811cd9904af70420eefd6ea11ef7da129f58835ff56b89faa637bc9ac2efaab903402229f491d8d3485261cd068699b6ba58a1ddbbef6db51e8fe34e8a78e542d7ba351c21ea8d8f1d29f5d5d15939487e27f4416b0ca632c59efd1b1eb66511a5a0fbf615b766c5862d0bd8a3fe7a0e0da0fb2fe1fcb19e8f9996a8ea0fccde538175238fc8b0ee6f29af7f642773ebe8cd5402415a01451a840476b2fceb0e388d30d4b376c37fe401c2a2c2f941dad179c540c1c8ce030d460c4d983be9ab0b20f69144c1ae13f9383ea1c08504fb0bf321503efe43488310dd8dc77ec5b8349b8bfe97c2c560ea878de87c11e3d597f1fea742d73eec7f37be43949ef1a0d15c3f3e3fc0a8335617055ac91328ec22b50fc15b941d3d1624cd88bc25f3e941fddc6200689581bfec416b4b2cb73";


    function expmod(bytes memory g, uint256 x, bytes memory p) public view returns ( bytes memory) {
        require(g.length == 384,"unqualified length of g");
        require(p.length == 384,"unqualified length of p");
        bytes memory input = abi.encodePacked(bytes32(g.length),abi.encode(0x20),bytes32(p.length),g,bytes32(x),p);
        bytes memory result = new bytes(384);
        bytes memory pointer = new bytes(384);
        assembly {
            if iszero(staticcall(sub(gas, 2000), 0x05, add(input,0x20), 0x380, add(pointer,0x20), 0x180 )) {
                revert(0, 0)
            }
        }
        for(uint i =0; i<12;i++) {
            bytes32 value;
            uint256 start = 32*i;
            assembly {
                value := mload(add(add(pointer,0x20),start))
            }
            for(uint j=0;j<32;j++) {
                result[start+j] = value[j];
            }
        }
        require(result.length == 384,"unqualified length of result");
        return result;
    }
   //////////////////////////////////////////
    function set_I1_batch(uint len, bytes32[] memory add, bytes32  [] memory val) public{
        for(uint i = 0; i < len; i++){
            bytes32 x = add[i];
            bytes32 y1 = val[3*i];
            bytes32 y2 = val[3*i+1];
            bytes32 y3 = val[3*i+2];
            t_T[x] = y1;
            t_f[x] = y2;
            t_p[x] = y3;
        }
    } 
    function set_I2_batch(uint len, bytes32[] memory add, bytes32  [] memory val) public{
        for(uint i = 0; i < len; i++){
            bytes32 x = add[i];
            bytes32 y1 = val[2*i];
            bytes32 y2 = val[2*i+1];
            l_v[x] = y1;
            l_c[x] = y2;
        }
    } 
   /////////////////////////////////////////

    
    function set_N(bytes32 add, uint256 val) public{
        N[add]=val;
    } 
    function set_Nbatch(uint len, bytes32[] memory add, uint256[] memory val) public{
        for(uint i = 0; i < len; i++){
            bytes32 x = add[i];
            uint256 y = val[i];
            N[x] = y;
        }
    } 

    function set_AL(uint256 add, bytes  memory val) public{
        AL[add]=val;
    } 

    function search(uint256 alpha,uint256 G_u_1,uint256 Hk,bytes32 [] memory Tk) public {
        int flag = 0;
        bytes  memory AI;
        AI = AL[G_u_1];
        // result1 = AI;
        require(pp.length == 384,"unqualified length of pp");
        // require(abi.encode(AI).length == 384,"unqualified length of AI");
  
        bytes  memory T = expmod(AI,Hk,pp);
        bytes32 t = keccak256(T);
        //R.push(t);
        if(t_T[t] != bytes32(0x0)){
        // if(I[t][0] != bytes32(0x0)){
            //判断 时间是否匹配
            M.push(1);
            for(uint i = 0; i < alpha; i++){
                if(t_f[t] == Tk[i]){
                // if(I[t][1] == Tk[i]){
                    flag = 1;
                    break;
                }
            }
        
            //取值
            if(flag == 1){
                M.push(2);
                bytes32 st =  t_p[t] ^ keccak256(T);
                bytes  memory st_0 = new bytes(32);
                for(uint j = 0;j < 32;j++){//进行赋值st_0 = 0||st
                    st_0[j] = st[j];
                    if(j==15){
                        st_0[j] = '0';
                    }
                }
                bytes32 l = keccak256(st_0);

                for( i = 0; i < N[t];i++){
                        M.push(3);
                        R.push(l_c[l]);
                        
                        //生成 1||st_0 ->H3
                        st_0[15] = '1';
                        //求出H(1||st)^v = st-1
                        bytes32 temp = l_v[l] ^ keccak256(st_0); 

                        //求st-1对应的l   并且 st_0 = 0||st-1 
                        for( j = 0;j < 16;j++){//进行赋值
                            st_0[j] = '0';
                        }
                        for( j = 16;j < 32;j++){//进行赋值
                            st_0[j] = temp[j];
                        }
                        // push c

                        l = keccak256(st_0);
                }
                

            }
        }
    }


    function retrieve2() public view returns(int256 [] memory){
        return M;
    }
   
    function retrieve0() public view returns(bytes32 [] memory){
        return R;
    }
  
}