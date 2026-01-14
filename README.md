# Vibe Check Polling API

A simple REST API for creating polls and casting votes.

## Features
- Create polls
- View poll results
- One vote per user per poll

## One Vote Logic
Each vote stores `(poll_id, user_id)` in a separate table.
If the same user tries to vote again on the same poll, the API blocks it.

## Live API
Deployed on Render.

Use `/docs` for API testing.
