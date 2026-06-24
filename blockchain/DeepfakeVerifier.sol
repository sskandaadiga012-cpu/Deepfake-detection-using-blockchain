// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract DeepfakeVerifier {

    mapping(bytes32 => bool) public isFakeMap;
    mapping(bytes32 => uint256) public timestampMap;
    mapping(bytes32 => string) public detectorMap;

    event VerificationStored(
        string videoHash,
        bool isFake,
        string detector,
        uint256 timestamp
    );

    function storeResult(
        string memory videoHash,
        bool isFake,
        string memory detector
    ) public {
        bytes32 key = keccak256(abi.encodePacked(videoHash));
        isFakeMap[key] = isFake;
        timestampMap[key] = block.timestamp;
        detectorMap[key] = detector;
        emit VerificationStored(videoHash, isFake, detector, block.timestamp);
    }

    function getResult(string memory videoHash)
        public view
        returns (bool, uint256, string memory)
    {
        bytes32 key = keccak256(abi.encodePacked(videoHash));
        return (isFakeMap[key], timestampMap[key], detectorMap[key]);
    }
}
