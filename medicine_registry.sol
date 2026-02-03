pragma solidity ^0.8.0;

contract MedicineRegistry {

    struct Drug {
        string name;
        string batch;
        string manufacturer;
        uint expiry;
    }

    mapping(bytes32 => Drug) public drugs;

    event DrugRegistered(bytes32 drugId);

    function registerDrug(
        string memory _name,
        string memory _batch,
        string memory _manufacturer,
        uint _expiry
    ) public returns (bytes32) {

        bytes32 drugId = keccak256(
            abi.encodePacked(_name, _batch, _manufacturer, _expiry, block.timestamp)
        );

        drugs[drugId] = Drug(_name, _batch, _manufacturer, _expiry);

        emit DrugRegistered(drugId);
        return drugId;
    }

    function getDrug(bytes32 _drugId)
        public view returns (string memory, string memory)
    {
        Drug memory d = drugs[_drugId];
        return (d.name, d.manufacturer);
    }
}
