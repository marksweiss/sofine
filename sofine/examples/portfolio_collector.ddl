-- NOTE: Assumes this was done previously
-- template0 thing necessary to override default encoding of SQL_ASCII with Postgres.app
-- create database sofine_portfolio with template = template0 owner=postgres encoding='UTF8';

\connect sofine_portfolio;

create table if not exists portfolio_data 
(
    updated timestamp default now(),
    key varchar(64) not null,
    attr_key varchar(64) not null,
    attr_value varchar(1024) not null,
    primary key (updated, key, attr_key)
);

